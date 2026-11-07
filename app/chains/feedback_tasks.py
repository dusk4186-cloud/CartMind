"""
LangChain agents and chains for Customer Feedback multi-stage processing.
Implements 3 dedicated, modular LangChain agents:
  • Task 1: Feedback Classification Agent (Review -> Sentiment, Categorization, Feedback Area)
  • Task 2: Auto-Reply Generation Agent (Review + Op/Task 1 -> Auto reply message)
  • Task 3: Workflow Routing Agent (Review + Op/Task 1 -> Routing action: Jira, ServiceNow, Customer service email, N/A)
"""

import logging
from typing import Dict, Any, Optional, Union
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from app.config import AgentConfig
from app.models.sentiment import (
    SentimentLabel,
    FeedbackType,
    FeedbackCategory,
    RoutingTarget,
    FeedbackRoutingAction,
    Task1ClassificationOutput,
    Task2AutoReplyOutput,
    Task3RoutingOutput,
    FeedbackPipelineResult,
)
from app.services.sentiment_service import SentimentService

logger = logging.getLogger(__name__)


_llm_cache: Dict[float, Any] = {}


def _get_llm(temperature: float = 0.0):
    """
    Lazily instantiate and cache preferred Chat model by temperature:
    1. ChatGroq if GROQ_API_KEY is configured (ultra-fast LPU inference, sub-second latency).
    2. ChatGoogleGenerativeAI if GOOGLE_API_KEY is configured.
    3. None (falls back to deterministic SentimentService engine).
    Reuses cached client instances to avoid redundant connection pool allocations.
    """
    if temperature in _llm_cache:
        return _llm_cache[temperature]

    groq_key = AgentConfig.get_groq_api_key()
    if groq_key and "your_actual" not in groq_key and ChatGroq is not None:
        try:
            client = ChatGroq(
                groq_api_key=groq_key,
                model_name=AgentConfig.get_groq_model(),
                temperature=temperature,
                max_retries=2,
                timeout=AgentConfig.get_timeout_seconds(),
            )
            _llm_cache[temperature] = client
            return client
        except Exception as e:
            logger.warning(f"Could not initialize ChatGroq, falling back to Gemini: {e}")

    api_key = AgentConfig.get_api_key()
    if api_key and "your_actual" not in api_key:
        try:
            client = ChatGoogleGenerativeAI(
                model=AgentConfig.get_model_name(),
                google_api_key=api_key,
                temperature=temperature,
                max_retries=2,
                timeout=AgentConfig.get_timeout_seconds(),
            )
            _llm_cache[temperature] = client
            return client
        except Exception as e:
            logger.warning(f"Could not initialize ChatGoogleGenerativeAI: {e}")
            return None

    return None


# ══════════════════════════════════════════════════════════════════════════
#  TASK 1: CLASSIFICATION AGENT (Review -> Sentiment, Categorization, Feedback Area)
# ══════════════════════════════════════════════════════════════════════════

TASK1_SYSTEM_PROMPT = """You are an expert customer feedback intelligence classifier for an e-commerce platform.
Analyze the customer review/feedback and accurately classify it across 3 dimensions:

1. Sentiment:
   - 'positive': Customer expresses happiness, satisfaction, or praise.
   - 'negative': Customer expresses dissatisfaction, frustration, complaints, or problems.
   - 'neutral': Objective observation without strong emotion.
   - 'sarcastic': Ironic remarks or false praise masking dissatisfaction (e.g., "The shoes are great, if you enjoy blisters", "Amazing quality if you like things that break in one day").

2. Categorization (Intent):
   - 'Statement': A descriptive observation about fit, style, or general experience without an active issue.
   - 'Complaint': Explicit grievance or sarcastic complaint demanding correction, replacement, refund, or expressing pain/disappointment.
   - 'Question': Inquiry seeking clarity, tracking status, or explanation.
   - 'Praise': Enthusiastic appreciation for the brand or product.
   - 'Suggestion': Feature request or recommendation for improvement.

3. Feedback Area (Aspect):
   - 'Quality': Product defects, damaged items, stitching, fabric, breakage, or finish.
   - 'Delivery': Shipment delays, courier tracking, packaging, transit times.
   - 'Pricing': Costs, discounts, overcharges, refund amounts.
   - 'Sizing': Fit issues, measurements, too tight/loose, blisters, rubbing, or physical discomfort.
   - 'Customer Service': Staff interaction, helpline, support representative.
   - 'N/A': General brand compliment or statement not targeting a specific operational issue.

CRITICAL RULES:
- Never take sarcastic praise literally. For example, "The shoes are great, if you enjoy blisters" or "This belt is so good, feeling like ants biting my waist" are Sentiment: 'sarcastic', Categorization: 'Complaint', and Feedback Area: 'Sizing'.
- Do NOT confuse genuine contextual recommendations with sarcasm: "Great shoes, if you love trekking" is genuine positive praise (Sentiment: 'positive', Categorization: 'Statement', Feedback Area: 'N/A'). Sarcasm only occurs when the condition represents a flaw, pain, or negative consequence.
- Provide diagnostic commentary explicitly highlighting the tone, sentiment, and whether an operational complaint exists.
"""

TASK1_PROMPT = ChatPromptTemplate.from_messages([
    ("system", TASK1_SYSTEM_PROMPT),
    ("human", "Classify this customer review:\n\"{review}\""),
])


class Task1ClassificationAgent:
    """
    LangChain Agent for Task 1:
    Input: {"review": str}
    Output: Task1ClassificationOutput (Sentiment, Categorization, Feedback Area)
    """

    def __init__(self, llm: Optional[Any] = None):
        self._llm = llm

    @property
    def llm(self) -> Optional[Any]:
        """Lazily initialize and return the LLM client on first access."""
        if self._llm is None:
            self._llm = _get_llm(temperature=0.0)
        return self._llm

    @llm.setter
    def llm(self, value: Optional[Any]) -> None:
        self._llm = value

    def invoke(self, inputs: Dict[str, Any]) -> Task1ClassificationOutput:
        """Execute Task 1 classification chain with resilient fallback."""
        review = inputs.get("review", "").strip()

        if self.llm is not None:
            try:
                structured_chain = TASK1_PROMPT | self.llm.with_structured_output(Task1ClassificationOutput)
                result = structured_chain.invoke({"review": review})
                if isinstance(result, Task1ClassificationOutput):
                    return result
            except Exception as e:
                logger.warning(f"Task 1 LLM chain invocation failed, using domain fallback: {e}")

        # Deterministic domain fallback using validated SentimentService
        card = SentimentService.classify_feedback(review)
        return Task1ClassificationOutput(
            sentiment=card.sentiment,
            categorization=card.feedback_type,
            feedback_area=card.category,
            commentary=card.commentary,
        )


# ══════════════════════════════════════════════════════════════════════════
#  TASK 2: AUTO-REPLY GENERATION AGENT (Review + Op/Task 1 -> Auto reply message)
# ══════════════════════════════════════════════════════════════════════════

TASK2_SYSTEM_PROMPT = """You are an empathetic, professional customer care auto-responder for an e-commerce brand.
Formulate a concise, brand-aligned suggested response based on the customer's Review and the Classification from Task 1.

Guidelines:
- If Sentiment is positive or Categorization is Praise/Statement:
  Express warm gratitude and appreciation (e.g. "Thank you for your feedback! We're glad you enjoyed your experience." or "We appreciate your kind words! Happy you loved it.").
- If Categorization is Complaint (e.g. damaged goods / quality issue):
  Acknowledge the inconvenience sincerely, apologize, and commit to immediate resolution (e.g. "We're sorry for the issue. We'll resolve this promptly.").
- If Categorization is Question (e.g. delivery delays):
  Apologize for the uncertainty/delay and assure that the matter is being investigated (e.g. "We apologize for the delay. We're investigating this matter.").
- If Sentiment is Sarcastic or involves discomfort/blisters:
  De-escalate with genuine empathy and transparent support. Acknowledge the discomfort/pain, apologize sincerely, and offer return/exchange assistance (e.g. "We sincerely apologize for the discomfort and inconvenience. We'll be glad to help arrange a return or exchange."). NEVER send cheerful praise or say "We're glad you enjoyed your experience" to sarcastic complaints!

Keep the response natural, polite, and under 30 words.
"""

TASK2_PROMPT = ChatPromptTemplate.from_messages([
    ("system", TASK2_SYSTEM_PROMPT),
    (
        "human",
        "Customer Review: \"{review}\"\n"
        "Task 1 Sentiment: {sentiment}\n"
        "Task 1 Categorization: {categorization}\n"
        "Task 1 Feedback Area: {feedback_area}\n\n"
        "Generate the appropriate auto reply message:",
    ),
])


class Task2AutoReplyAgent:
    """
    LangChain Agent for Task 2:
    Input: {"review": str, "sentiment": str, "categorization": str, "feedback_area": str} (Review + Op/Task 1)
    Output: Task2AutoReplyOutput (Auto reply message)
    """

    def __init__(self, llm: Optional[Any] = None):
        self._llm = llm

    @property
    def llm(self) -> Optional[Any]:
        """Lazily initialize and return the LLM client on first access."""
        if self._llm is None:
            self._llm = _get_llm(temperature=0.2)
        return self._llm

    @llm.setter
    def llm(self, value: Optional[Any]) -> None:
        self._llm = value

    def invoke(self, inputs: Dict[str, Any]) -> Task2AutoReplyOutput:
        """Generate auto-reply message based on review and Task 1 classification."""
        review = inputs.get("review", "").strip()
        sentiment = str(inputs.get("sentiment", "positive"))
        categorization = str(inputs.get("categorization", "Statement"))
        feedback_area = str(inputs.get("feedback_area", "N/A"))

        if self.llm is not None:
            try:
                structured_chain = TASK2_PROMPT | self.llm.with_structured_output(Task2AutoReplyOutput)
                result = structured_chain.invoke({
                    "review": review,
                    "sentiment": sentiment,
                    "categorization": categorization,
                    "feedback_area": feedback_area,
                })
                if isinstance(result, Task2AutoReplyOutput):
                    return result
            except Exception as e:
                logger.warning(f"Task 2 LLM chain invocation failed, using domain fallback: {e}")

        # Deterministic domain fallback matching UI design cards
        card = SentimentService.classify_feedback(review)
        return Task2AutoReplyOutput(auto_reply_message=card.suggested_response)


# ══════════════════════════════════════════════════════════════════════════
#  TASK 3: WORKFLOW ROUTING AGENT (Review + Op/Task 1 -> Routing action)
# ══════════════════════════════════════════════════════════════════════════

TASK3_SYSTEM_PROMPT = """You are an automated workflow dispatch agent for an e-commerce support system.
Determine the correct operational routing action and destination platform based on the Review and the Classification from Task 1.

Destinations:
1. 'ServiceNow':
   - Physical product damage, defect on arrival, broken components, replacement requests, warranty claims.
   - Routing Action label: "ServiceNow escalation"

2. 'Customer service email':
   - Sizing issues, blisters, fit discomfort, return/exchange assistance, shipping delays, courier tracking, order status inquiries, logistics updates, general support questions, and de-escalation of sarcastic complaints.
   - Routing Action label: "Forward to customer support engineer"

3. 'Jira':
   - Software bugs, app crashes, website checkout failures, cart discount errors, catalog data glitches.
   - Routing Action label: "Jira bug ticket"

4. 'N/A':
   - Positive feedback, brand praise, general statements without actionable customer problems.
   - Routing Action label: "N/A"

Priority levels: 'critical', 'high', 'medium', 'low', 'none'.
Provide clear diagnostic reasoning for the chosen routing destination.
"""

TASK3_PROMPT = ChatPromptTemplate.from_messages([
    ("system", TASK3_SYSTEM_PROMPT),
    (
        "human",
        "Customer Review: \"{review}\"\n"
        "Task 1 Sentiment: {sentiment}\n"
        "Task 1 Categorization: {categorization}\n"
        "Task 1 Feedback Area: {feedback_area}\n\n"
        "Determine the routing action and destination platform:",
    ),
])


class Task3RoutingAgent:
    """
    LangChain Agent for Task 3:
    Input: {"review": str, "sentiment": str, "categorization": str, "feedback_area": str} (Review + Op/Task 1)
    Output: Task3RoutingOutput (Routing action, routing target: Jira, ServiceNow, Customer service email, N/A)
    """

    def __init__(self, llm: Optional[Any] = None):
        self._llm = llm

    @property
    def llm(self) -> Optional[Any]:
        """Lazily initialize and return the LLM client on first access."""
        if self._llm is None:
            self._llm = _get_llm(temperature=0.0)
        return self._llm

    @llm.setter
    def llm(self, value: Optional[Any]) -> None:
        self._llm = value

    def invoke(self, inputs: Dict[str, Any]) -> Task3RoutingOutput:
        """Determine routing action and platform target based on review and Task 1 classification."""
        review = inputs.get("review", "").strip()
        review_lower = review.lower()
        sentiment = str(inputs.get("sentiment", "")).lower()
        categorization = str(inputs.get("categorization", ""))
        feedback_area = str(inputs.get("feedback_area", ""))

        if self.llm is not None:
            try:
                structured_chain = TASK3_PROMPT | self.llm.with_structured_output(Task3RoutingOutput)
                result = structured_chain.invoke({
                    "review": review,
                    "sentiment": sentiment,
                    "categorization": categorization,
                    "feedback_area": feedback_area,
                })
                if isinstance(result, Task3RoutingOutput):
                    return result
            except Exception as e:
                logger.warning(f"Task 3 LLM chain invocation failed, using domain fallback: {e}")

        # Deterministic domain rule dispatch
        if any(w in review_lower for w in ["app crash", "checkout bug", "error 500", "website bug", "glitch", "broken link", "api error"]):
            return Task3RoutingOutput(
                routing_action="Jira bug ticket",
                routing_target=RoutingTarget.JIRA,
                priority="high",
                reason=f"Technical issue or platform defect reported in review: '{review}'. Dispatched to engineering backlog in Jira.",
            )

        if (
            feedback_area == FeedbackCategory.SIZING.value
            or "blister" in review_lower
            or "blisters" in review_lower
            or "ants biting" in review_lower
            or "biting" in review_lower
            or "tight" in review_lower
            or (sentiment == "sarcastic" and any(w in review_lower for w in ["blister", "waist", "belt", "shoe", "fit"]))
        ):
            return Task3RoutingOutput(
                routing_action="Forward to customer support engineer",
                routing_target=RoutingTarget.CUSTOMER_SERVICE_EMAIL,
                priority="high",
                reason=f"Sizing, fit discomfort, or physical irritation reported ('{review}'). Dispatched to customer service email for exchange and resolution.",
            )

        if categorization == FeedbackType.COMPLAINT.value or feedback_area == FeedbackCategory.QUALITY.value or "damaged" in review_lower or "replace" in review_lower:
            if sentiment in ("negative", "sarcastic") or "damaged" in review_lower:
                return Task3RoutingOutput(
                    routing_action="ServiceNow escalation",
                    routing_target=RoutingTarget.SERVICENOW,
                    priority="high",
                    reason=f"Quality defect or damaged product reported ('{review}'). Dispatched to ServiceNow for replacement processing.",
                )

        if categorization == FeedbackType.QUESTION.value or feedback_area == FeedbackCategory.DELIVERY.value or "delayed" in review_lower or "shipping" in review_lower:
            return Task3RoutingOutput(
                routing_action="Forward to customer support engineer",
                routing_target=RoutingTarget.CUSTOMER_SERVICE_EMAIL,
                priority="medium",
                reason=f"Delivery or tracking inquiry requiring investigation ('{review}'). Dispatched to customer service email queue.",
            )

        return Task3RoutingOutput(
            routing_action="N/A",
            routing_target=RoutingTarget.NOT_APPLICABLE,
            priority="none",
            reason=f"No operational escalation required for positive or informational statement ('{review}').",
        )


# ══════════════════════════════════════════════════════════════════════════
#  PIPELINE EXECUTOR (Task 1 -> Task 2 & Task 3)
# ══════════════════════════════════════════════════════════════════════════

def run_feedback_pipeline(
    review: str,
    task1_agent: Optional[Task1ClassificationAgent] = None,
    task2_agent: Optional[Task2AutoReplyAgent] = None,
    task3_agent: Optional[Task3RoutingAgent] = None,
) -> FeedbackPipelineResult:
    """
    Executes the 3 LangChain agents in pipeline sequence:
      1. Task 1 classifies Review into {sentiment, categorization, feedback_area}
      2. Task 2 generates Auto reply message using Review + Op/Task 1
      3. Task 3 determines Routing action (Jira / ServiceNow / Customer service email) using Review + Op/Task 1
    """
    t1 = task1_agent or Task1ClassificationAgent()
    t2 = task2_agent or Task2AutoReplyAgent()
    t3 = task3_agent or Task3RoutingAgent()

    # Step 1: Run Task 1
    task1_output = t1.invoke({"review": review})

    # Step 2 & 3: Run Task 2 & Task 3 with Review + Op/Task 1
    t2_inputs = {
        "review": review,
        "sentiment": task1_output.sentiment.value if hasattr(task1_output.sentiment, "value") else str(task1_output.sentiment),
        "categorization": task1_output.categorization.value if hasattr(task1_output.categorization, "value") else str(task1_output.categorization),
        "feedback_area": task1_output.feedback_area.value if hasattr(task1_output.feedback_area, "value") else str(task1_output.feedback_area),
    }

    task2_output = t2.invoke(t2_inputs)
    task3_output = t3.invoke(t2_inputs)

    return FeedbackPipelineResult(
        review=review,
        task1=task1_output,
        task2=task2_output,
        task3=task3_output,
    )
