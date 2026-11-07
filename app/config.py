"""
Configuration module for the LangChain agent and external service integrations.
Safely loads environment variables, validates required credentials, and ensures zero secret leakage.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Locate and load .env file from project root or parent workspace
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
PARENT_ENV_PATH = PROJECT_ROOT.parent / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
elif PARENT_ENV_PATH.exists():
    load_dotenv(dotenv_path=PARENT_ENV_PATH)
else:
    load_dotenv()


class AgentConfig:
    """Central configuration class providing validated environment settings."""

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Retrieves Google Gemini API key from GOOGLE_API_KEY or GEMINI_API_KEY."""
        return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    @classmethod
    def get_groq_api_key(cls) -> Optional[str]:
        """Retrieves Groq API key from GROQ_API_KEY."""
        return os.getenv("GROQ_API_KEY")

    @classmethod
    def get_groq_model(cls) -> str:
        """Returns verified Groq model identifier."""
        return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

    @classmethod
    def get_model_name(cls) -> str:
        """Returns verified Gemini model identifier."""
        return os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

    @classmethod
    def get_fastapi_base_url(cls) -> str:
        """Returns URL of the running FastAPI mock e-commerce backend."""
        base_url = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        return base_url

    @classmethod
    def get_max_iterations(cls) -> int:
        """Configurable upper bound on ReAct agent tool invocation cycles."""
        try:
            return int(os.getenv("AGENT_MAX_ITERATIONS", "8"))
        except ValueError:
            return 8

    @classmethod
    def get_timeout_seconds(cls) -> float:
        """HTTP client request timeout in seconds."""
        try:
            return float(os.getenv("API_TIMEOUT_SECONDS", "30.0"))
        except ValueError:
            return 30.0

    @classmethod
    def get_langsmith_api_key(cls) -> Optional[str]:
        """Retrieves LangSmith API key from LANGCHAIN_API_KEY or LANGSMITH_API_KEY."""
        return os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")

    @classmethod
    def get_langsmith_project(cls) -> str:
        """Retrieves configured LangSmith project name."""
        return os.getenv("LANGCHAIN_PROJECT", "ecommerce-cx-intelligence")

    @classmethod
    def is_langsmith_enabled(cls) -> bool:
        """Returns True if LangSmith tracing is active."""
        tracing_val = os.getenv("LANGCHAIN_TRACING_V2", "false").lower()
        key = cls.get_langsmith_api_key()
        return tracing_val in ("true", "1", "yes") and bool(key and "your_actual" not in key)

    @classmethod
    def validate(cls) -> None:
        """
        Validates presence of required configuration.
        Raises ValueError with helpful setup instructions without exposing any secrets.
        """
        key = cls.get_api_key()
        if not key or not key.strip() or "your_actual" in key:
            raise ValueError(
                "Missing or invalid Google Gemini API Key. "
                "Please configure 'GOOGLE_API_KEY' in your .env file."
            )

    @classmethod
    def get_safe_summary(cls) -> Dict[str, Any]:
        """Returns non-sensitive configuration summary safe for logging or user display."""
        key = cls.get_api_key()
        is_configured = bool(key and len(key.strip()) > 10)
        return {
            "model": cls.get_model_name(),
            "backend_url": cls.get_fastapi_base_url(),
            "max_iterations": cls.get_max_iterations(),
            "timeout_seconds": cls.get_timeout_seconds(),
            "api_key_configured": is_configured,
            "langsmith_enabled": cls.is_langsmith_enabled(),
            "langsmith_project": cls.get_langsmith_project() if cls.is_langsmith_enabled() else None,
        }
