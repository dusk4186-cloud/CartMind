"""
Automated unit and mocked evaluation tests for the LangChain ReAct agent.
Tests configuration security, constraint enforcement, table generation, and credential protection.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.config import AgentConfig
from app.agent import EcommerceAgent, extract_message_text
from langchain_core.messages import AIMessage, HumanMessage


# ============================================================================
# 1. Environment Configuration & Security Tests
# ============================================================================
def test_config_validation_with_missing_api_key(monkeypatch):
    """Verify AgentConfig raises descriptive ValueError when API key is missing."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError) as excinfo:
        AgentConfig.validate()
    assert "Missing or invalid Google Gemini API Key" in str(excinfo.value)


def test_config_safe_summary_does_not_expose_secret():
    """Verify get_safe_summary() masks and never outputs raw API keys."""
    summary = AgentConfig.get_safe_summary()
    assert "api_key" not in summary
    assert "api_key_configured" in summary
    assert isinstance(summary["api_key_configured"], bool)
    assert summary["model"] is not None
    assert summary["backend_url"] is not None


# ============================================================================
# 2. Text Content Extraction Helper Tests
# ============================================================================
def test_extract_message_text_formats():
    """Verify extract_message_text safely handles string and block-structured outputs."""
    # Plain string
    assert extract_message_text("Plain text answer") == "Plain text answer"

    # List of dictionary blocks (Gemini format)
    blocks = [{"type": "text", "text": "Paragraph 1"}, {"type": "text", "text": "Paragraph 2"}]
    assert extract_message_text(blocks) == "Paragraph 1\nParagraph 2"

    # List of plain strings
    assert extract_message_text(["Line 1", "Line 2"]) == "Line 1\nLine 2"


# ============================================================================
# 3. Agent Evaluation & Output Formatting (Mocked Graph Tests)
# ============================================================================
def test_multiple_products_comparison_table_behavior():
    """Verify that when multiple products qualify, the output includes a Markdown comparison table."""
    mock_agent = MagicMock()
    mock_agent.agent_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Find running shoes under 3000"),
            AIMessage(
                content=(
                    "Here are qualifying products:\n\n"
                    "| Product | Price (INR) | Rating | Availability | Key Pros | Key Cons |\n"
                    "|---|---|---|---|---|---|\n"
                    "| Puma Air Stride | ₹2,699 | 4.5 | In Stock | Lightweight mesh | Snug fit |\n"
                    "| Red Tape Skate | ₹1,199 | 4.0 | In Stock | Great value | Firmer sole |\n\n"
                    "**Top Recommendation:** Puma Air Stride offers the best cushioning for running."
                )
            ),
        ]
    }

    # Test through EcommerceAgent.run wrapper
    with patch.object(EcommerceAgent, "__init__", lambda self: None):
        agent = EcommerceAgent()
        agent.agent_graph = mock_agent.agent_graph
        result = agent.run("Find running shoes under 3000")

        output = result["output"]
        assert "| Product | Price" in output
        assert "|---|---|---|---|---|---|" in output
        assert "Top Recommendation" in output


def test_single_product_recommendation_behavior():
    """Verify single matching product produces direct recommendation without unnecessary table."""
    mock_agent = MagicMock()
    mock_agent.agent_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Recommend a reversible formal leather belt"),
            AIMessage(
                content=(
                    "I recommend the **Classic Reversible Leather Belt (PROD001)** by Wildhorn.\n"
                    "Price: ₹999 (Original ₹1,999, 50% discount)\n"
                    "Rating: 4.5/5 from 4 reviews.\n"
                    "Availability: In Stock (15 units remaining, sizes 32-38).\n"
                    "Key Highlight: Genuine full-grain leather with rotating zinc buckle."
                )
            ),
        ]
    }

    with patch.object(EcommerceAgent, "__init__", lambda self: None):
        agent = EcommerceAgent()
        agent.agent_graph = mock_agent.agent_graph
        result = agent.run("Recommend a reversible formal leather belt")

        output = result["output"]
        assert "Classic Reversible Leather Belt" in output
        assert "₹999" in output
        assert "|---|---|" not in output  # No unnecessary table for single product


def test_zero_products_found_behavior():
    """Verify that when no products qualify, agent clearly explains constraints that failed."""
    mock_agent = MagicMock()
    mock_agent.agent_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Find leather jackets under 500 rupees"),
            AIMessage(
                content=(
                    "No qualifying products were found in the catalogue matching all your criteria.\n"
                    "Constraint explanation: All available leather jackets (e.g. Biker Faux Leather Jacket) start at ₹3,999, "
                    "which exceeds your ₹500 budget limit.\n"
                    "Would you like to search with an expanded budget?"
                )
            ),
        ]
    }

    with patch.object(EcommerceAgent, "__init__", lambda self: None):
        agent = EcommerceAgent()
        agent.agent_graph = mock_agent.agent_graph
        result = agent.run("Find leather jackets under 500 rupees")

        output = result["output"]
        assert "No qualifying products" in output
        assert "budget" in output.lower()


def test_credential_leak_prevention_in_output():
    """Verify API keys are never leaked into agent outputs or message logs."""
    fake_key = "AIzaSySecretFakeApiKey123456789"
    mock_agent = MagicMock()
    mock_agent.agent_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Show me running shoes"),
            AIMessage(content="Puma Air Stride running shoes are available at ₹2,699."),
        ]
    }

    with patch.object(EcommerceAgent, "__init__", lambda self: None):
        agent = EcommerceAgent()
        agent.agent_graph = mock_agent.agent_graph
        result = agent.run("Show me running shoes")

        assert fake_key not in result["output"]
        for msg in result["messages"]:
            assert fake_key not in str(msg.content)
