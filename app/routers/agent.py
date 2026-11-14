"""
Agent Router exposing conversational AI and LangGraph feedback workflows over REST.
Allows external frontends (Next.js, mobile apps, React) to interact with CartMind agents.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.agent import EcommerceAgent
from app.output_sanitizer import OutputSanitizer
from app.config import AgentConfig
from app.graphs.feedback_graph import get_feedback_workflow

router = APIRouter(prefix="/api/agent", tags=["Agent"])

# Global agent instance cache
_agent_instance: Optional[EcommerceAgent] = None


def get_agent() -> EcommerceAgent:
    """Retrieve or lazily initialize the singleton EcommerceAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        AgentConfig.validate()
        _agent_instance = EcommerceAgent()
    return _agent_instance


# ── Request / Response Models ──────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer shopping query or support request")
    chat_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Previous message history (role & content pairs)"
    )


class ChatResponse(BaseModel):
    reply: str
    chat_history: List[Dict[str, Any]]
    model: str
    blocked_by_security: bool = False


class FeedbackAnalysisRequest(BaseModel):
    review: str = Field(..., min_length=1, description="Customer review text to analyze")


class BatchFeedbackRequest(BaseModel):
    reviews: List[str] = Field(..., min_length=1, description="List of reviews to process concurrently")
    max_workers: int = Field(default=5, ge=1, le=10)


# ── Endpoints ──────────────────────────────────────────────────────────

def serialize_message(m: Any) -> Dict[str, Any]:
    """Serialize LangChain BaseMessage objects into JSON-safe dictionaries."""
    if isinstance(m, dict):
        return m
    cls_name = m.__class__.__name__
    if cls_name == "HumanMessage":
        role = "user"
    elif cls_name == "AIMessage":
        role = "assistant"
    elif cls_name == "ToolMessage":
        role = "tool"
    else:
        role = "system"

    content = getattr(m, "content", str(m))
    if isinstance(content, list):
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        content = " ".join(p for p in parts if p)

    return {"role": role, "content": str(content)}


@router.post("/chat", response_model=ChatResponse, summary="Chat with CartMind Shopping Assistant")
def chat_with_agent(req: ChatRequest):
    """
    Submits a user query through CartMind's input security gate, executes the
    LangChain ReAct agent with tools, sanitizes the output, and returns the formatted response.
    """
    prompt = req.message.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Input Gate: Pre-process user query (pure probe refusal or stealth clause stripping)
    clean_query, refusal = OutputSanitizer.sanitize_user_input(prompt)
    if refusal:
        return ChatResponse(
            reply=refusal,
            chat_history=req.chat_history,
            model=AgentConfig.get_model_name(),
            blocked_by_security=True,
        )

    active_prompt = clean_query if clean_query else prompt

    try:
        agent = get_agent()
        result = agent.run(active_prompt, chat_history=req.chat_history)
        output = result.get("output", "I was unable to generate a response for your query.")

        # 3. Output Sanitizer
        sanitized_output = OutputSanitizer.sanitize_output(output, original_query=prompt)
        raw_msgs = result.get("messages", [])[-10:]
        updated_history = [serialize_message(m) for m in raw_msgs]

        return ChatResponse(
            reply=sanitized_output,
            chat_history=updated_history,
            model=AgentConfig.get_model_name(),
            blocked_by_security=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")


@router.post("/feedback/analyze", summary="Analyze a Single Customer Review via LangGraph")
def analyze_single_feedback(req: FeedbackAnalysisRequest):
    """
    Invokes the LangGraph 3-task feedback workflow on Groq LPU:
    Sentiment detection, suggested response generation, and enterprise support routing.
    """
    review_text = req.review.strip()
    if not review_text:
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")

    try:
        wf = get_feedback_workflow()
        res = wf.invoke(review_text)

        target_val = res.task3.routing_target.value if hasattr(res.task3.routing_target, "value") else str(res.task3.routing_target)

        return {
            "review": review_text,
            "sentiment": {
                "sentiment": res.task1.sentiment.value,
                "categorization": res.task1.categorization.value,
                "feedback_area": res.task1.feedback_area.value,
                "commentary": res.task1.commentary,
            },
            "suggested_response": res.task2.auto_reply_message,
            "routing": {
                "routing_target": target_val,
                "routing_action": res.task3.routing_action,
                "priority": res.task3.priority,
                "reason": res.task3.reason,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback analysis error: {str(e)}")


@router.post("/feedback/batch", summary="Process Multiple Reviews Concurrently via LangGraph")
def analyze_batch_feedback(req: BatchFeedbackRequest):
    """
    Executes concurrent batch processing of customer reviews with aggregated analytics.
    """
    try:
        wf = get_feedback_workflow()
        batch_res = wf.batch(req.reviews, max_workers=req.max_workers)
        return batch_res.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch feedback processing error: {str(e)}")
