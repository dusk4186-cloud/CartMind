"""
Promptfoo Python Provider for E-Commerce Assistant Security & Output Sanitizer Testing.
Executes EcommerceAgent with OutputSanitizer on test prompts and returns clean output.
"""

import sys
import os
import contextlib
import io
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import EcommerceAgent

# Initialize cached agent instance
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = EcommerceAgent()
    return _agent


def call_api(prompt: str, options: dict = None, context: dict = None) -> dict:
    """
    Standard Promptfoo Python provider entrypoint.
    Executes EcommerceAgent on prompt and returns output for test assertions.
    """
    agent = get_agent()
    # Prompt can come directly or via context vars
    query = prompt
    if context and "vars" in context and "query" in context["vars"]:
        query = context["vars"]["query"]

    try:
        # Suppress any library stdout/stderr messages
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = agent.run(query)
            output = result.get("output", "")
        return {"output": output}
    except Exception as e:
        return {"error": str(e), "output": f"Error: {str(e)}"}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_q = " ".join(sys.argv[1:])
        res = call_api(test_q)
        print(res.get("output", ""))
    else:
        print("Usage: python promptfoo_provider.py <query>")
