"""
LangGraph state graph controller orchestrating the 3 LangChain feedback agents:
  • Task 1: Classification Agent (Review -> Sentiment, Categorization, Feedback Area)
  • Task 2: Auto-Reply Agent (Review + Op/Task 1 -> Auto reply message)
  • Task 3: Routing Agent (Review + Op/Task 1 -> Routing action: Jira, ServiceNow, Customer service email, N/A)

Graph Topology:
                 START
                   │
                   ▼
               [classify] (Task 1)
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    [auto_reply]         [routing] (Task 2 & Task 3 parallel fan-out)
         │                   │
         └─────────┬─────────┘
                   ▼
                  END
"""

import logging
from typing import TypedDict, Optional, Dict, Any, Generator
from langgraph.graph import StateGraph, START, END

from app.models.sentiment import (
    SentimentLabel,
    FeedbackType,
    FeedbackCategory,
    RoutingTarget,
    Task1ClassificationOutput,
    Task2AutoReplyOutput,
    Task3RoutingOutput,
    FeedbackPipelineResult,
    BatchFeedbackResult,
)
from app.chains.feedback_tasks import (
    Task1ClassificationAgent,
    Task2AutoReplyAgent,
    Task3RoutingAgent,
)

logger = logging.getLogger(__name__)


class FeedbackGraphState(TypedDict, total=False):
    """Execution state managed across the LangGraph controller."""
    review: str
    task1: Optional[Task1ClassificationOutput]
    task2: Optional[Task2AutoReplyOutput]
    task3: Optional[Task3RoutingOutput]
    error: Optional[str]


def make_task1_node(agent: Optional[Task1ClassificationAgent] = None):
    """Creates Node 1: Task 1 Classification execution with lazy agent loading."""
    _agent = agent

    def task1_node(state: FeedbackGraphState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = Task1ClassificationAgent()
        review = state.get("review", "")
        try:
            output = _agent.invoke({"review": review})
            return {"task1": output}
        except Exception as e:
            logger.error(f"Error in task1_node: {e}")
            return {"error": f"Task 1 Error: {str(e)}"}

    return task1_node


def make_task2_node(agent: Optional[Task2AutoReplyAgent] = None):
    """Creates Node 2: Task 2 Auto-Reply generation with lazy agent loading."""
    _agent = agent

    def task2_node(state: FeedbackGraphState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = Task2AutoReplyAgent()
        review = state.get("review", "")
        task1 = state.get("task1")

        sentiment_val = task1.sentiment.value if task1 and hasattr(task1.sentiment, "value") else "positive"
        categorization_val = task1.categorization.value if task1 and hasattr(task1.categorization, "value") else "Statement"
        feedback_area_val = task1.feedback_area.value if task1 and hasattr(task1.feedback_area, "value") else "N/A"

        try:
            output = _agent.invoke({
                "review": review,
                "sentiment": sentiment_val,
                "categorization": categorization_val,
                "feedback_area": feedback_area_val,
            })
            return {"task2": output}
        except Exception as e:
            logger.error(f"Error in task2_node: {e}")
            return {"error": f"Task 2 Error: {str(e)}"}

    return task2_node


def make_task3_node(agent: Optional[Task3RoutingAgent] = None):
    """Creates Node 3: Task 3 Workflow Routing decision with lazy agent loading."""
    _agent = agent

    def task3_node(state: FeedbackGraphState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = Task3RoutingAgent()
        review = state.get("review", "")
        task1 = state.get("task1")

        sentiment_val = task1.sentiment.value if task1 and hasattr(task1.sentiment, "value") else "positive"
        categorization_val = task1.categorization.value if task1 and hasattr(task1.categorization, "value") else "Statement"
        feedback_area_val = task1.feedback_area.value if task1 and hasattr(task1.feedback_area, "value") else "N/A"

        try:
            output = _agent.invoke({
                "review": review,
                "sentiment": sentiment_val,
                "categorization": categorization_val,
                "feedback_area": feedback_area_val,
            })
            return {"task3": output}
        except Exception as e:
            logger.error(f"Error in task3_node: {e}")
            return {"error": f"Task 3 Error: {str(e)}"}

    return task3_node


def build_feedback_graph(
    task1_agent: Optional[Task1ClassificationAgent] = None,
    task2_agent: Optional[Task2AutoReplyAgent] = None,
    task3_agent: Optional[Task3RoutingAgent] = None,
):
    """
    Builds and compiles the LangGraph StateGraph.
    Connects:
      START -> classify (Task 1)
      classify -> auto_reply (Task 2)
      classify -> routing (Task 3)
      auto_reply -> END
      routing -> END
    """
    builder = StateGraph(FeedbackGraphState)

    builder.add_node("classify", make_task1_node(task1_agent))
    builder.add_node("auto_reply", make_task2_node(task2_agent))
    builder.add_node("routing", make_task3_node(task3_agent))

    builder.add_edge(START, "classify")
    builder.add_edge("classify", "auto_reply")
    builder.add_edge("classify", "routing")
    builder.add_edge("auto_reply", END)
    builder.add_edge("routing", END)

    return builder.compile()


class FeedbackWorkflowGraph:
    """
    LangGraph Workflow Controller encapsulating the compiled StateGraph.
    Provides convenient execution, streaming, and pipeline output formatting.
    Implements lazy compilation: StateGraph is only built and compiled when accessed.
    """

    def __init__(
        self,
        task1_agent: Optional[Task1ClassificationAgent] = None,
        task2_agent: Optional[Task2AutoReplyAgent] = None,
        task3_agent: Optional[Task3RoutingAgent] = None,
    ):
        self.task1_agent = task1_agent
        self.task2_agent = task2_agent
        self.task3_agent = task3_agent
        self._compiled_graph = None

    @property
    def compiled_graph(self):
        """Lazily compiles and caches the StateGraph on first access."""
        if self._compiled_graph is None:
            self._compiled_graph = build_feedback_graph(
                task1_agent=self.task1_agent,
                task2_agent=self.task2_agent,
                task3_agent=self.task3_agent,
            )
        return self._compiled_graph

    @compiled_graph.setter
    def compiled_graph(self, value):
        self._compiled_graph = value

    def invoke(self, review: str) -> FeedbackPipelineResult:
        """
        Executes the LangGraph controller for a customer review.
        Returns validated FeedbackPipelineResult containing outputs from all 3 tasks.
        """
        run_config = {
            "run_name": "FeedbackWorkflowPipeline",
            "tags": ["sentiment-analysis", "cx-intelligence", "langgraph"],
        }
        raw_state = self.compiled_graph.invoke({"review": review}, config=run_config)

        task1 = raw_state.get("task1")
        task2 = raw_state.get("task2")
        task3 = raw_state.get("task3")

        # Fallback guards in case of unexpected state disruption
        if task1 is None:
            t1 = self.task1_agent or Task1ClassificationAgent()
            task1 = t1.invoke({"review": review})
        if task2 is None:
            t2 = self.task2_agent or Task2AutoReplyAgent()
            task2 = t2.invoke({
                "review": review,
                "sentiment": task1.sentiment.value,
                "categorization": task1.categorization.value,
                "feedback_area": task1.feedback_area.value,
            })
        if task3 is None:
            t3 = self.task3_agent or Task3RoutingAgent()
            task3 = t3.invoke({
                "review": review,
                "sentiment": task1.sentiment.value,
                "categorization": task1.categorization.value,
                "feedback_area": task1.feedback_area.value,
            })

        return FeedbackPipelineResult(
            review=review,
            task1=task1,
            task2=task2,
            task3=task3,
        )

    def batch(self, reviews: list, max_workers: int = 5) -> BatchFeedbackResult:
        """
        Executes the LangGraph controller concurrently across a batch of customer reviews.
        Returns aggregated summary statistics and per-item classifications.
        """
        import time
        from concurrent.futures import ThreadPoolExecutor

        start_time = time.perf_counter()
        clean_reviews = [r.strip() for r in reviews if r and str(r).strip()]

        if not clean_reviews:
            return BatchFeedbackResult(
                total_processed=0,
                results=[],
                sentiment_distribution={},
                category_distribution={},
                routing_distribution={},
                escalations_count=0,
                processing_time_ms=0.0,
            )

        with ThreadPoolExecutor(max_workers=min(max_workers, len(clean_reviews))) as executor:
            results = list(executor.map(self.invoke, clean_reviews))

        # Compute summary metrics
        sentiment_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        routing_counts: Dict[str, int] = {}
        escalations = 0

        for res in results:
            s_val = res.task1.sentiment.value if hasattr(res.task1.sentiment, "value") else str(res.task1.sentiment)
            c_val = res.task1.feedback_area.value if hasattr(res.task1.feedback_area, "value") else str(res.task1.feedback_area)
            r_val = res.task3.routing_target.value if hasattr(res.task3.routing_target, "value") else str(res.task3.routing_target)

            sentiment_counts[s_val] = sentiment_counts.get(s_val, 0) + 1
            category_counts[c_val] = category_counts.get(c_val, 0) + 1
            routing_counts[r_val] = routing_counts.get(r_val, 0) + 1

            if r_val in ("ServiceNow", "Customer service email") or res.task3.priority in ("high", "critical"):
                escalations += 1

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return BatchFeedbackResult(
            total_processed=len(results),
            results=results,
            sentiment_distribution=sentiment_counts,
            category_distribution=category_counts,
            routing_distribution=routing_counts,
            escalations_count=escalations,
            processing_time_ms=elapsed_ms,
        )

    def stream_steps(self, review: str) -> Generator[Dict[str, Any], None, None]:
        """
        Streams intermediate node updates as each agent completes execution in the graph.
        """
        run_config = {
            "run_name": "StreamFeedbackWorkflowPipeline",
            "tags": ["sentiment-analysis", "cx-intelligence", "langgraph", "streaming"],
        }
        for step in self.compiled_graph.stream({"review": review}, config=run_config):
            yield step

    async def ainvoke(self, review: str) -> FeedbackPipelineResult:
        """
        Asynchronously executes the LangGraph controller for a customer review.
        Returns validated FeedbackPipelineResult containing outputs from all 3 tasks.
        """
        run_config = {
            "run_name": "AsyncFeedbackWorkflowPipeline",
            "tags": ["sentiment-analysis", "cx-intelligence", "langgraph", "async"],
        }
        raw_state = await self.compiled_graph.ainvoke({"review": review}, config=run_config)

        task1 = raw_state.get("task1")
        task2 = raw_state.get("task2")
        task3 = raw_state.get("task3")

        # Fallback guards in case of unexpected state disruption
        if task1 is None:
            t1 = self.task1_agent or Task1ClassificationAgent()
            task1 = t1.invoke({"review": review})
        if task2 is None:
            t2 = self.task2_agent or Task2AutoReplyAgent()
            task2 = t2.invoke({
                "review": review,
                "sentiment": task1.sentiment.value,
                "categorization": task1.categorization.value,
                "feedback_area": task1.feedback_area.value,
            })
        if task3 is None:
            t3 = self.task3_agent or Task3RoutingAgent()
            task3 = t3.invoke({
                "review": review,
                "sentiment": task1.sentiment.value,
                "categorization": task1.categorization.value,
                "feedback_area": task1.feedback_area.value,
            })

        return FeedbackPipelineResult(
            review=review,
            task1=task1,
            task2=task2,
            task3=task3,
        )

    async def astream_steps(self, review: str):
        """
        Asynchronously streams intermediate node updates as each agent completes execution in the graph.
        """
        run_config = {
            "run_name": "AsyncStreamFeedbackWorkflowPipeline",
            "tags": ["sentiment-analysis", "cx-intelligence", "langgraph", "streaming", "async"],
        }
        async for step in self.compiled_graph.astream({"review": review}, config=run_config):
            yield step

    async def abatch(self, reviews: list, max_concurrency: int = 5) -> BatchFeedbackResult:
        """
        Asynchronously executes the LangGraph controller concurrently across a batch of customer reviews
        using asyncio.gather and an asyncio.Semaphore for bounded concurrency.
        """
        import asyncio
        import time

        start_time = time.perf_counter()
        clean_reviews = [r.strip() for r in reviews if r and str(r).strip()]

        if not clean_reviews:
            return BatchFeedbackResult(
                total_processed=0,
                results=[],
                sentiment_distribution={},
                category_distribution={},
                routing_distribution={},
                escalations_count=0,
                processing_time_ms=0.0,
            )

        sem = asyncio.Semaphore(max_concurrency)

        async def _bounded_invoke(rev: str) -> FeedbackPipelineResult:
            async with sem:
                return await self.ainvoke(rev)

        results = await asyncio.gather(*[_bounded_invoke(r) for r in clean_reviews])

        # Compute summary metrics
        sentiment_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        routing_counts: Dict[str, int] = {}
        escalations = 0

        for res in results:
            s_val = res.task1.sentiment.value if hasattr(res.task1.sentiment, "value") else str(res.task1.sentiment)
            c_val = res.task1.feedback_area.value if hasattr(res.task1.feedback_area, "value") else str(res.task1.feedback_area)
            r_val = res.task3.routing_target.value if hasattr(res.task3.routing_target, "value") else str(res.task3.routing_target)

            sentiment_counts[s_val] = sentiment_counts.get(s_val, 0) + 1
            category_counts[c_val] = category_counts.get(c_val, 0) + 1
            routing_counts[r_val] = routing_counts.get(r_val, 0) + 1

            if r_val in ("ServiceNow", "Customer service email") or res.task3.priority in ("high", "critical"):
                escalations += 1

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return BatchFeedbackResult(
            total_processed=len(results),
            results=results,
            sentiment_distribution=sentiment_counts,
            category_distribution=category_counts,
            routing_distribution=routing_counts,
            escalations_count=escalations,
            processing_time_ms=elapsed_ms,
        )

    @staticmethod
    def get_mermaid_diagram() -> str:
        """Returns Mermaid diagram string visualizing the graph topology."""
        return (
            "graph TD\n"
            "    START([START]) --> classify[Task 1: Classification Agent]\n"
            "    classify --> auto_reply[Task 2: Auto-Reply Agent]\n"
            "    classify --> routing[Task 3: Workflow Routing Agent]\n"
            "    auto_reply --> END([END])\n"
            "    routing --> END([END])\n"
            "    style classify fill:#2563eb,stroke:#1d4ed8,color:#fff\n"
            "    style auto_reply fill:#14b8a6,stroke:#0d9488,color:#fff\n"
            "    style routing fill:#f59e0b,stroke:#d97706,color:#fff\n"
        )


_shared_workflow_instance: Optional[FeedbackWorkflowGraph] = None


def get_feedback_workflow() -> FeedbackWorkflowGraph:
    """
    Returns a lazily-initialized shared singleton FeedbackWorkflowGraph.
    Avoids redundant StateGraph compilation across requests while maintaining lazy evaluation.
    """
    global _shared_workflow_instance
    if _shared_workflow_instance is None:
        _shared_workflow_instance = FeedbackWorkflowGraph()
    return _shared_workflow_instance
