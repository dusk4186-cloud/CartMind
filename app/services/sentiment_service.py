"""
Sentiment and Sarcasm Analysis Service for E-commerce Reviews and User Feedback.
Implements a hybrid architecture:
1. Fast, deterministic rule & lexicon engine for sub-millisecond offline classification and sarcasm detection.
2. Optional LLM-assisted deep context evaluation when active.
"""

import re
from datetime import datetime, timezone
import random
from typing import List, Dict, Any, Optional, Tuple, Union
from app.models.sentiment import (
    SentimentLabel,
    EscalationReason,
    EscalationUrgency,
    FeedbackType,
    FeedbackCategory,
    FeedbackRoutingAction,
    ReviewSentiment,
    ProductSentimentSummary,
    UserFeedbackSentiment,
    FeedbackClassification,
    SupportTicketRequest,
    SupportTicket,
)
from app.services.product_service import ProductService
from app.data.mock_data import REVIEWS


# ─────────────────────────────────────────────────────────────────────────────
# LEXICONS & PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

POSITIVE_WORDS = {
    "exceptional", "great", "love", "loved", "loves", "durable", "smooth",
    "perfect", "perfectly", "premium", "sturdy", "comfortable", "luxury",
    "fantastic", "excellent", "clean", "breathable", "lightweight", "best",
    "awesome", "high-quality", "recommended", "elegant", "flawless", "superb",
    "satisfying", "convenient", "reliable", "rich", "cushioned", "delighted",
    "pleased", "worth", "stylish", "brilliant", "solid", "responsive",
    "decent", "fine", "okay", "light",
}

NEGATIVE_WORDS = {
    "stiff", "broke", "broken", "cheap", "tear", "tears", "tore", "fake",
    "poor", "poorly", "terrible", "worst", "awful", "disappointed", "disappointing",
    "uncomfortable", "flimsy", "heavy", "small", "tight", "rough", "scratched",
    "damaged", "waste", "wasted", "horrible", "return", "returned", "useless",
    "cardboard", "plastic", "snag", "faded", "crease", "defective", "bad",
    "overpriced", "hate", "hated", "ridiculous", "rubbish", "fail", "failed",
    "blister", "blisters", "pain", "hurt", "hurts", "pinch", "rubbing", "bruise",
    "biting", "bite", "bites", "ants", "sting", "stinging", "itch", "itchy", "scratching",
}

CONTRAST_CONJUNCTIONS = {
    "but", "however", "although", "except", "unfortunately", "though", "yet", "whereas",
}

# Explicit sarcastic phrases common in e-commerce complaints
SARCASTIC_PHRASES = [
    r"lightning (fast|speed).*(week|month|day)",
    r"took (only|just) \d+ (week|month|day)s?",
    r"(great|amazing|wonderful|perfect|awesome|fantastic|love (it|them|this)|good).*?if you (like|enjoy|love|want|prefer)\s+(blister|blisters|pain|sweat|break|broke|wait|waiting|headache|waste|disappointment|garbage|trash|burn|bite|biting|sting|itch|itching|scratch|rubbing|pinch|bruise)",
    r"if you (like|enjoy|love|want|prefer)\s+(blister|blisters|pain|sweat|break|wait|headache|waste|disappointment|garbage|trash|bite|biting)",
    r"(so|too|very)?\s*(good|great|amazing|wonderful|perfect|love).*?(like ants|ants biting|needles|stabbing|killing my|pinching|hurting)",
    r"(feels?|feeling)\s+like\s+ants\s+biting",
    r"ants\s+biting",
    r"what a (masterpiece|joke|brilliant design)",
    r"truly amazing.*broke",
    r"so glad i wasted",
    r"what a genius idea",
    r"pure genius to make",
    r"works wonderfully.*\.\.\.",
    r"glad you find it",
    r"outstanding quality.*fell apart",
    r"world class.*trash",
    r"amazing.*zero.*stock",
    r"great job on having.*(none|zero|no)",
]

# Aspect keyword mappings
ASPECT_KEYWORDS = {
    "quality": ["leather", "material", "finish", "craftsmanship", "stitching", "build", "fabric"],
    "sizing": ["size", "sizes", "fit", "fitting", "tight", "loose", "small", "large", "waist", "shoe size", "blister", "blisters", "rubbing", "pinch", "belt", "ants biting", "biting"],
    "durability": ["durable", "sturdy", "broke", "broken", "tear", "lasts", "flimsy", "longevity"],
    "buckle": ["buckle", "ratchet", "swivel", "clasp", "hardware"],
    "comfort": ["comfortable", "comfort", "cushion", "cushioning", "stiff", "rough", "soft", "breathable", "lightweight", "blister", "blisters", "pain", "hurt", "ants biting", "biting", "itch", "stinging"],
    "price_value": ["price", "discount", "value", "worth", "expensive", "cheap", "cost"],
}


class SentimentService:
    """Core analysis engine for review sentiment, sarcasm detection, and user tone calibration."""

    @classmethod
    def _detect_sarcasm(cls, text: str, rating: Optional[float] = None) -> Tuple[bool, float, Optional[str]]:
        """
        Detects sarcasm using lexical contrasts, ironic hyperbole, and rating/text mismatches.

        Returns:
            Tuple of (is_sarcastic, confidence, translated_meaning)
        """
        text_lower = text.lower()

        # Rule 1: Check known sarcastic idioms/regexes
        for pattern in SARCASTIC_PHRASES:
            if re.search(pattern, text_lower):
                return True, 0.95, f"Customer is expressing ironic frustration regarding: '{text.strip()}'"

        # Rule 2: Low star rating (<= 2.5) paired with hyperbolic praise words
        if rating is not None and rating <= 2.5:
            superlatives = {"amazing", "lightning", "masterpiece", "genius", "pure gold", "best ever", "love it", "fantastic"}
            found_superlatives = [w for w in superlatives if w in text_lower]
            if found_superlatives:
                return (
                    True,
                    0.90,
                    f"Low rating ({rating}★) paired with ironic praise '{found_superlatives[0]}'; signifies a major complaint.",
                )

        # Rule 3: Scare quotes around quality terms (e.g., 'premium' or "quality") with negative sentiment
        scare_quote_pattern = r'["\'](premium|genuine|quality|durable|luxury)["\']'
        if re.search(scare_quote_pattern, text_lower):
            has_neg = any(w in text_lower for w in NEGATIVE_WORDS)
            if has_neg or (rating is not None and rating <= 3.0):
                return True, 0.85, "Customer placed quotation marks around marketing claims to mock product quality."

        return False, 0.0, None

    @classmethod
    def _extract_aspects(cls, text: str) -> List[str]:
        """Extracts product attributes referenced in the comment text."""
        text_lower = text.lower()
        found_aspects = []
        for aspect, keywords in ASPECT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                found_aspects.append(aspect)
        return found_aspects

    @classmethod
    def classify_review(cls, review: Union[Dict[str, Any], Any]) -> ReviewSentiment:
        """
        Classifies an individual customer review into a SentimentLabel with score and sarcasm detection.
        """
        if isinstance(review, dict):
            r_id = review.get("review_id", "REV_UNKNOWN")
            reviewer = review.get("reviewer_name", "Anonymous")
            rating = float(review.get("rating", 3.0))
            comment = review.get("comment", "")
        else:
            r_id = getattr(review, "review_id", "REV_UNKNOWN")
            reviewer = getattr(review, "reviewer_name", "Anonymous")
            rating = float(getattr(review, "rating", 3.0))
            comment = getattr(review, "comment", "")

        comment_clean = comment.strip()
        words = re.findall(r"\b[a-zA-Z-]+\b", comment_clean.lower())

        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        has_contrast = any(c in words for c in CONTRAST_CONJUNCTIONS)

        # Sarcasm detection
        is_sarcastic, sarcasm_conf, _ = cls._detect_sarcasm(comment_clean, rating=rating)

        # Base valence calculation (-1.0 to 1.0)
        # Normalize rating from 1..5 to -1..+1 scale
        rating_score = (rating - 3.0) / 2.0
        word_delta = (pos_count - neg_count) / max(len(words), 1) * 3.0
        combined_score = max(-1.0, min(1.0, (rating_score * 0.6) + (word_delta * 0.4)))

        # Determine sentiment label
        if is_sarcastic:
            label = SentimentLabel.SARCASTIC
            confidence = max(0.85, sarcasm_conf)
            sentiment_score = -abs(combined_score) if combined_score > 0 else combined_score
        elif has_contrast and pos_count > 0 and neg_count > 0:
            label = SentimentLabel.MIXED
            confidence = 0.85
            sentiment_score = combined_score
        elif rating <= 2.0 or (rating <= 2.5 and neg_count >= pos_count):
            label = SentimentLabel.NEGATIVE
            confidence = 0.85 if rating <= 2.0 else 0.75
            sentiment_score = combined_score
        elif rating >= 4.5 or (rating >= 4.0 and pos_count >= neg_count):
            label = SentimentLabel.POSITIVE
            confidence = 0.90 if rating >= 4.5 else 0.80
            sentiment_score = combined_score
        elif 2.5 <= rating <= 3.5 and abs(pos_count - neg_count) <= 1:
            label = SentimentLabel.NEUTRAL
            confidence = 0.80
            sentiment_score = combined_score
        elif neg_count > pos_count:
            label = SentimentLabel.NEGATIVE
            confidence = 0.75
            sentiment_score = combined_score
        elif pos_count > neg_count:
            label = SentimentLabel.POSITIVE
            confidence = 0.75
            sentiment_score = combined_score
        else:
            label = SentimentLabel.NEUTRAL
            confidence = 0.70
            sentiment_score = combined_score

        key_aspects = cls._extract_aspects(comment_clean)

        return ReviewSentiment(
            review_id=r_id,
            reviewer_name=reviewer,
            rating=rating,
            comment=comment_clean,
            sentiment=label,
            sentiment_score=round(sentiment_score, 2),
            confidence=round(confidence, 2),
            is_sarcastic=is_sarcastic,
            key_aspects=key_aspects,
        )

    @classmethod
    def analyze_product_reviews(cls, product_id: str) -> Optional[ProductSentimentSummary]:
        """
        Aggregates and summarizes all customer review sentiments for a given product ID.
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        # Gather reviews matching product ID
        matching_reviews = [
            r for r in REVIEWS
            if r["product_id"].upper() == product.product_id.upper()
        ]

        if not matching_reviews:
            return ProductSentimentSummary(
                product_id=product.product_id,
                product_name=product.name,
                total_reviews_analyzed=0,
                overall_sentiment=SentimentLabel.NEUTRAL,
                average_sentiment_score=0.0,
                sentiment_distribution={"positive": 0, "negative": 0, "neutral": 0, "sarcastic": 0, "mixed": 0},
                positive_percentage=0.0,
                negative_percentage=0.0,
                neutral_percentage=0.0,
                sarcastic_percentage=0.0,
                mixed_percentage=0.0,
                key_praises=[],
                key_complaints=[],
                sarcastic_warnings=[],
                recommended_agent_tone="No customer reviews are available yet. Recommend based strictly on specifications.",
            )

        classified: List[ReviewSentiment] = [cls.classify_review(r) for r in matching_reviews]
        total = len(classified)

        # Count distributions
        distribution = {
            "positive": sum(1 for c in classified if c.sentiment == SentimentLabel.POSITIVE),
            "negative": sum(1 for c in classified if c.sentiment == SentimentLabel.NEGATIVE),
            "neutral": sum(1 for c in classified if c.sentiment == SentimentLabel.NEUTRAL),
            "sarcastic": sum(1 for c in classified if c.sentiment == SentimentLabel.SARCASTIC),
            "mixed": sum(1 for c in classified if c.sentiment == SentimentLabel.MIXED),
        }

        avg_score = round(sum(c.sentiment_score for c in classified) / total, 2)

        # Determine dominant sentiment
        dominant_label = max(distribution, key=distribution.get)
        overall_sentiment = SentimentLabel(dominant_label)

        # Extract praises, complaints, and sarcastic warnings
        praises = []
        complaints = []
        sarcastic_warnings = []

        for c in classified:
            if c.sentiment == SentimentLabel.POSITIVE:
                praises.append(f"{c.reviewer_name} ({c.rating}★): \"{c.comment}\"")
            elif c.sentiment == SentimentLabel.NEGATIVE:
                complaints.append(f"{c.reviewer_name} ({c.rating}★): \"{c.comment}\"")
            elif c.sentiment == SentimentLabel.SARCASTIC:
                sarcastic_warnings.append(
                    f"Flagged Sarcasm from {c.reviewer_name} ({c.rating}★): \"{c.comment}\" — Interpret as genuine user dissatisfaction."
                )
            elif c.sentiment == SentimentLabel.MIXED:
                # Capture both sides
                praises.append(f"{c.reviewer_name} (mixed): \"{c.comment}\"")

        # Recommended agent tone guidance
        if distribution["sarcastic"] > 0:
            tone = (
                f"Be cautious: {distribution['sarcastic']} review(s) contain sarcastic complaints. "
                "Do not present ironic statements as positive highlights. Acknowledge customer feedback transparently."
            )
        elif distribution["negative"] > distribution["positive"]:
            tone = "Adopt a critical, objective tone. Clearly highlight the common complaints before recommending."
        elif distribution["positive"] >= total * 0.75:
            tone = "Confidently recommend with an upbeat tone, highlighting strong customer satisfaction and verified quality."
        else:
            tone = "Provide a balanced, neutral assessment weighing both pros and cons objectively."

        return ProductSentimentSummary(
            product_id=product.product_id,
            product_name=product.name,
            total_reviews_analyzed=total,
            overall_sentiment=overall_sentiment,
            average_sentiment_score=avg_score,
            sentiment_distribution=distribution,
            positive_percentage=round((distribution["positive"] / total) * 100, 1),
            negative_percentage=round((distribution["negative"] / total) * 100, 1),
            neutral_percentage=round((distribution["neutral"] / total) * 100, 1),
            sarcastic_percentage=round((distribution["sarcastic"] / total) * 100, 1),
            mixed_percentage=round((distribution["mixed"] / total) * 100, 1),
            key_praises=praises[:4],
            key_complaints=complaints[:4],
            sarcastic_warnings=sarcastic_warnings,
            recommended_agent_tone=tone,
        )

    @classmethod
    def analyze_user_query(cls, query: str) -> UserFeedbackSentiment:
        """
        Analyzes the emotional tone, frustration, sarcasm, and human escalation triggers
        of live shopper chat input. Returns tailored tone guidance for the conversational assistant.
        """
        query_clean = query.strip()
        query_lower = query_clean.lower()
        words = re.findall(r"\b[a-zA-Z-]+\b", query_lower)

        # Check for sarcasm in user prompt
        is_sarcastic, _, _ = cls._detect_sarcasm(query_clean)

        # Sarcastic chat patterns
        user_sarcastic_cues = [
            "great job on having", "wonderful service", "amazing how", "oh perfect",
            "oh wonderful", "love how nothing", "thanks for nothing", "super helpful",
        ]
        if any(cue in query_lower for cue in user_sarcastic_cues) and any(w in query_lower for w in ["zero", "none", "no", "broke", "bad", "wrong", "out of stock"]):
            is_sarcastic = True

        frustration_words = {"ridiculous", "annoying", "waste", "terrible", "worst", "hate", "useless", "scam", "frustrated", "fed up"}
        frustration_hits = sum(1 for w in words if w in frustration_words)

        if frustration_hits >= 2 or re.search(r"[!?]{2,}", query):
            frustration_level = "high"
        elif frustration_hits == 1 or "disappointed" in query_lower:
            frustration_level = "mild"
        else:
            frustration_level = "none"

        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        # ─────────────────────────────────────────────────────────────────
        # Human Escalation & Handover Trigger Evaluation
        # ─────────────────────────────────────────────────────────────────
        needs_human = False
        escalation_reason: Optional[EscalationReason] = None
        escalation_urgency: Optional[EscalationUrgency] = None

        # 1. Extreme legal / fraud threats
        if re.search(r"\b(sue you|consumer court|consumer forum|lawsuit|lawyer|police|cheaters|scammers|taking legal action)\b", query_lower):
            needs_human = True
            escalation_reason = EscalationReason.HIGH_FRUSTRATION
            escalation_urgency = EscalationUrgency.CRITICAL
        # 2. Billing / Payment / Double Charge / Refund issues
        elif re.search(r"\b(charged twice|double charged|overcharged|unauthorized charge|wrong amount|money (was )?deducted|debited from (my|the) account|payment failed.*money deducted|refund status|where is my refund|issue (a )?refund)\b", query_lower):
            needs_human = True
            escalation_reason = EscalationReason.BILLING_OR_PAYMENT_DISPUTE
            escalation_urgency = EscalationUrgency.HIGH
        # 3. Damaged or missing shipment
        elif re.search(r"\b(arrived broken|damaged package|package (is )?damaged|broken item|empty box|order (is )?(missing|lost)|never arrived|package not delivered|item missing from|wrong item delivered)\b", query_lower):
            needs_human = True
            escalation_reason = EscalationReason.ORDER_DAMAGE_OR_MISSING
            escalation_urgency = EscalationUrgency.HIGH
        # 4. Policy exceptions, bulk orders, wholesale, B2B
        elif re.search(r"\b(bulk order|wholesale|tax exempt|corporate discount|b2b order|custom size|bespoke)\b", query_lower):
            needs_human = True
            escalation_reason = EscalationReason.POLICY_EXCEPTION
            escalation_urgency = EscalationUrgency.MEDIUM
        # 5. Explicit human agent requests
        elif (
            re.search(r"\b(talk|speak|connect|transfer)\b.*?\b(to|with)?\b.*?\b(human|person|agent|representative|rep|supervisor|manager|operator|support executive)\b", query_lower)
            or re.search(r"\b(customer care|customer support|human agent|live person|real person|talk to someone|speak to someone)\b", query_lower)
            or re.search(r"\b(want|need) a human\b", query_lower)
            or re.search(r"\bcall (me|support)\b", query_lower)
        ):
            needs_human = True
            escalation_reason = EscalationReason.EXPLICIT_HUMAN_REQUEST
            escalation_urgency = EscalationUrgency.HIGH if frustration_level == "high" else EscalationUrgency.MEDIUM

        # Determine sentiment & tone advice
        if needs_human:
            sentiment = SentimentLabel.NEGATIVE if frustration_level in ("mild", "high") else SentimentLabel.NEUTRAL
            tone_advice = (
                f"The shopper requires human assistance ({escalation_reason.value}). "
                "Invoke the 'escalate_to_human_support' tool to generate an authoritative support ticket. "
                "Provide the generated Ticket ID, assigned department, estimated wait time, and toll-free helpline number. "
                "Maintain a calm, empathetic, and reassuring professional demeanor."
            )
        elif is_sarcastic:
            sentiment = SentimentLabel.SARCASTIC
            tone_advice = (
                "The shopper is using sarcasm or irony to express dissatisfaction. "
                "DO NOT take sarcastic praise literally. Courteously acknowledge the inconvenience, "
                "validate their frustration with empathy, and directly offer actionable assistance or alternatives."
            )
        elif frustration_level == "high" or (neg_count > pos_count and frustration_level == "mild"):
            sentiment = SentimentLabel.NEGATIVE
            tone_advice = (
                "The shopper is frustrated or dissatisfied. Respond with a calm, empathetic, "
                "and solution-oriented tone. Avoid promotional fluff; focus on resolving their problem, "
                "finding available alternatives, or clarifying return/warranty options."
            )
        elif pos_count > neg_count and frustration_level == "none":
            sentiment = SentimentLabel.POSITIVE
            tone_advice = (
                "The shopper has positive intent or enthusiasm. Respond with a warm, engaging, "
                "and helpful shopping tone. Confirm their specifications and suggest relevant complementary items."
            )
        else:
            sentiment = SentimentLabel.NEUTRAL
            tone_advice = (
                "The shopper is asking a straightforward, objective question. "
                "Provide a direct, concise, and informative response supported by catalogue data."
            )

        # Run comprehensive feedback classification
        feedback_diag = cls.classify_feedback(query_clean)

        return UserFeedbackSentiment(
            query=query_clean,
            sentiment=sentiment,
            is_sarcastic=is_sarcastic,
            frustration_level=frustration_level,
            needs_human_escalation=needs_human,
            escalation_reason=escalation_reason,
            escalation_urgency=escalation_urgency,
            tone_advice=tone_advice,
            feedback_type=feedback_diag.feedback_type,
            category=feedback_diag.category,
            feedback_commentary=feedback_diag.commentary,
            suggested_response=feedback_diag.suggested_response,
            routing_action=feedback_diag.routing_action,
        )

    @classmethod
    def classify_feedback(cls, text: str, review_id: Optional[str] = None) -> FeedbackClassification:
        """
        Performs multi-dimensional classification of customer feedback or review.
        Extracts Sentiment, Feedback Type (Intent), Category (Aspect), generates
        diagnostic commentary, suggests a tailored response, and assigns routing actions.
        """
        text_clean = text.strip()
        text_lower = text_clean.lower()
        words = re.findall(r"\b[a-zA-Z-]+\b", text_lower)

        # 1. Sentiment detection
        is_sarcastic, _, _ = cls._detect_sarcasm(text_clean)
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        if is_sarcastic:
            sentiment = SentimentLabel.SARCASTIC
        elif any(w in text_lower for w in ["damaged", "broken", "delayed", "terrible", "waste", "poor", "hate", "scam"]):
            sentiment = SentimentLabel.NEGATIVE
        elif neg_count > pos_count:
            sentiment = SentimentLabel.NEGATIVE
        elif pos_count > neg_count or any(w in text_lower for w in ["love", "loved", "perfect", "fits perfectly", "premium"]):
            sentiment = SentimentLabel.POSITIVE
        else:
            sentiment = SentimentLabel.NEUTRAL

        # 2. Category / Aspect detection
        if any(w in text_lower for w in ["delay", "delayed", "shipping", "delivery", "courier", "tracking", "two weeks", "dispatch"]):
            category = FeedbackCategory.DELIVERY
        elif any(w in text_lower for w in ["damaged", "broken", "tear", "tears", "defective", "faulty", "scratched", "flimsy", "poor quality", "replace"]):
            category = FeedbackCategory.QUALITY
        elif any(w in text_lower for w in ["price", "cost", "expensive", "charged", "refund", "billing", "payment", "overpriced"]):
            category = FeedbackCategory.PRICING
        elif any(w in text_lower for w in ["tight", "loose", "wrong size", "too small", "too big", "sizing issue", "blister", "blisters", "pinch", "rubbing", "ants biting", "biting", "waist", "belt"]):
            category = FeedbackCategory.SIZING
        elif any(w in text_lower for w in ["customer service", "agent", "support representative", "helpline", "executive"]):
            category = FeedbackCategory.CUSTOMER_SERVICE
        elif sentiment == SentimentLabel.POSITIVE:
            # Positive appreciation statements like "fits perfectly and feels premium" or "stylish and durable" have N/A category
            category = FeedbackCategory.NOT_APPLICABLE
        elif any(w in text_lower for w in ["quality", "finish", "stitching", "durability"]):
            category = FeedbackCategory.QUALITY
        else:
            category = FeedbackCategory.NOT_APPLICABLE

        # 3. Feedback Type / Intent detection
        is_question = "?" in text_clean or bool(re.search(r"\b(what happened|why is|when will|where is|how do|can i|could you|is there)\b", text_lower))
        has_imperative_complaint = bool(re.search(r"\b(please replace|replace it|refund me|give me my|fix this|cancel my)\b", text_lower))
        has_suggestion = bool(re.search(r"\b(please add|would be (great|better|nice)|suggest|suggestion|hope you (make|add)|feature request)\b", text_lower))

        if is_question:
            feedback_type = FeedbackType.QUESTION
        elif has_imperative_complaint or (category in (FeedbackCategory.QUALITY, FeedbackCategory.DELIVERY, FeedbackCategory.SIZING) and sentiment in (SentimentLabel.NEGATIVE, SentimentLabel.SARCASTIC)) or sentiment == SentimentLabel.SARCASTIC:
            feedback_type = FeedbackType.COMPLAINT
        elif has_suggestion:
            feedback_type = FeedbackType.SUGGESTION
        elif sentiment == SentimentLabel.POSITIVE:
            feedback_type = FeedbackType.STATEMENT
        else:
            feedback_type = FeedbackType.STATEMENT

        # 4. Routing Action & Escalation
        if sentiment == SentimentLabel.SARCASTIC:
            routing_action = FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
            needs_escalation = True
        elif feedback_type == FeedbackType.COMPLAINT and category == FeedbackCategory.QUALITY:
            routing_action = FeedbackRoutingAction.SERVICENOW_ESCALATION
            needs_escalation = True
        elif feedback_type == FeedbackType.COMPLAINT and category == FeedbackCategory.SIZING:
            routing_action = FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
            needs_escalation = True
        elif (feedback_type == FeedbackType.QUESTION and category == FeedbackCategory.DELIVERY) or ("delayed" in text_lower):
            routing_action = FeedbackRoutingAction.FORWARD_TO_SUPPORT_ENGINEER
            needs_escalation = True
        elif category == FeedbackCategory.PRICING and sentiment == SentimentLabel.NEGATIVE:
            routing_action = FeedbackRoutingAction.BILLING_SPECIALIST_HANDOVER
            needs_escalation = True
        elif feedback_type == FeedbackType.SUGGESTION:
            routing_action = FeedbackRoutingAction.STORE_OPERATIONS_REVIEW
            needs_escalation = False
        else:
            routing_action = FeedbackRoutingAction.NOT_APPLICABLE
            needs_escalation = False

        # 5. Suggested Response
        if is_sarcastic or sentiment == SentimentLabel.SARCASTIC:
            suggested_response = "We sincerely apologize for the discomfort and inconvenience. We'll be glad to help arrange a return or exchange."
        elif feedback_type == FeedbackType.COMPLAINT and category == FeedbackCategory.QUALITY:
            suggested_response = "We're sorry for the issue. We'll resolve this promptly."
        elif feedback_type == FeedbackType.QUESTION and category == FeedbackCategory.DELIVERY:
            suggested_response = "We apologize for the delay. We're investigating this matter."
        elif "fits perfectly" in text_lower or "feels premium" in text_lower:
            suggested_response = "We appreciate your kind words! Happy you loved it."
        elif sentiment == SentimentLabel.POSITIVE:
            suggested_response = "Thank you for your feedback! We're glad you enjoyed your experience."
        elif feedback_type == FeedbackType.QUESTION:
            suggested_response = "Thank you for reaching out. We are glad to help clarify your question."
        else:
            suggested_response = "Thank you for sharing your feedback with us."

        # 6. Commentary on type of feedback
        if sentiment == SentimentLabel.SARCASTIC:
            commentary = (
                f"Customer used sarcastic irony ('{text_clean}') to express dissatisfaction and discomfort. "
                f"This is an implicit Complaint regarding {category.value}. Assigned routing: {routing_action.value}."
            )
        elif feedback_type == FeedbackType.COMPLAINT:
            commentary = (
                f"Customer has submitted a direct Complaint regarding product {category.value} "
                f"('{text_clean}'). The customer is seeking immediate redress or replacement. "
                f"Assigned routing: {routing_action.value}."
            )
        elif feedback_type == FeedbackType.QUESTION:
            commentary = (
                f"Customer has raised an inquiry Question concerning {category.value} "
                f"('{text_clean}'). The customer is seeking situational clarity and order tracking updates. "
                f"Assigned routing: {routing_action.value}."
            )
        elif feedback_type == FeedbackType.STATEMENT:
            commentary = (
                f"Customer has provided a descriptive Statement reflecting product satisfaction "
                f"and experience. Validates craftsmanship and catalog appeal. No operational escalation needed."
            )
        elif feedback_type == FeedbackType.PRAISE:
            commentary = (
                f"Customer has provided enthusiastic Praise. Reflects high brand loyalty and satisfaction. "
                f"No operational escalation needed."
            )
        else:
            commentary = (
                f"Customer has provided a {feedback_type.value} regarding {category.value}. "
                f"Assigned routing: {routing_action.value}."
            )

        return FeedbackClassification(
            feedback_id=review_id,
            text=text_clean,
            sentiment=sentiment,
            feedback_type=feedback_type,
            category=category,
            commentary=commentary,
            suggested_response=suggested_response,
            routing_action=routing_action,
            needs_escalation=needs_escalation,
        )

    @classmethod
    def get_sample_feedback_cards(cls) -> List[FeedbackClassification]:
        """
        Returns the 4 canonical customer feedback classification cards matching the design specification.
        """
        samples = [
            ("REVIEW 01", "Absolutely love this brand! The wallet I bought is stylish and durable."),
            ("REVIEW 02", "The leather jacket fits perfectly and feels premium."),
            ("REVIEW 03", "The jacket arrived damaged, please replace it."),
            ("REVIEW 04", "My order was delayed by two weeks, what happened?"),
        ]
        return [cls.classify_feedback(text, review_id=r_id) for r_id, text in samples]

    @classmethod
    def create_support_ticket(cls, request: SupportTicketRequest) -> SupportTicket:
        """
        Generates an authoritative support ticket for human escalation handover.
        """
        ticket_num = random.randint(10000, 99999)
        ticket_id = f"TKT-{ticket_num}"

        dept_map = {
            EscalationReason.BILLING_OR_PAYMENT_DISPUTE: "Billing & Financial Reconciliation",
            EscalationReason.ORDER_DAMAGE_OR_MISSING: "Logistics & Fulfillment Claims",
            EscalationReason.HIGH_FRUSTRATION: "Executive Customer Relations",
            EscalationReason.EXPLICIT_HUMAN_REQUEST: "Live Customer Care",
            EscalationReason.POLICY_EXCEPTION: "Store Management & Operations",
            EscalationReason.OTHER: "General Customer Support",
        }
        assigned_team = dept_map.get(request.category, "General Customer Support")

        wait_time_map = {
            EscalationUrgency.CRITICAL: 3,
            EscalationUrgency.HIGH: 5,
            EscalationUrgency.MEDIUM: 10,
            EscalationUrgency.LOW: 20,
        }
        wait_minutes = wait_time_map.get(request.urgency, 10)

        now_iso = datetime.now(timezone.utc).isoformat()

        return SupportTicket(
            ticket_id=ticket_id,
            category=request.category,
            urgency=request.urgency,
            issue_summary=request.issue_summary,
            status="OPEN",
            estimated_wait_minutes=wait_minutes,
            assigned_team=assigned_team,
            support_phone="+1 (800) 555-0199",
            support_email="priority-support@smartstore.example.com",
            created_at=now_iso,
        )
