"""
Terminal-based conversational CLI interface for the LangChain E-Commerce Agent.
Enables real-time interactive shopping discovery, comparison table rendering, and multi-turn follow-up conversations.
"""

import sys
import httpx

# Reconfigure stdout to UTF-8 for proper Unicode display (e.g. Rupee symbol ₹) on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.config import AgentConfig
from app.agent import EcommerceAgent


def print_banner(config_summary: dict):
    print("=" * 72)
    print("   🛒 AGENTIC AI SMART SHOPPING ASSISTANT (LangChain + Gemini Flash)   ")
    print("=" * 72)
    print(f"  * Model:           {config_summary['model']}")
    print(f"  * Backend Target:  {config_summary['backend_url']}")
    print(f"  * Max Iterations:  {config_summary['max_iterations']}")
    print(f"  * API Key Set:     {'Yes' if config_summary['api_key_configured'] else 'No'}")
    print("=" * 72)
    print("Type your shopping request below (e.g. 'Find comfortable black shoes under 3000').")
    print("Type 'exit', 'quit', or 'q' to leave.\n")


def check_backend_liveness(base_url: str):
    """Checks whether the mock e-commerce FastAPI backend is online."""
    try:
        r = httpx.get(f"{base_url}/health", timeout=3.0)
        if r.status_code == 200:
            print(f"[Backend Online] Connected to {base_url} ({r.json().get('catalog_size', 0)} items loaded).\n")
            return True
        else:
            print(f"[Warning] Backend responded with status {r.status_code} at {base_url}.\n")
            return False
    except Exception:
        print(f"[Warning] Could not reach backend at {base_url}. Start it with:\n    uvicorn app.main:app --reload\n")
        return False


def main():
    try:
        AgentConfig.validate()
    except ValueError as val_err:
        print(f"\n[Configuration Error] {val_err}\n")
        sys.exit(1)

    summary = AgentConfig.get_safe_summary()
    print_banner(summary)
    check_backend_liveness(summary["backend_url"])

    try:
        agent = EcommerceAgent()
    except Exception as init_err:
        print(f"[Agent Initialization Failed] {init_err}")
        sys.exit(1)

    chat_history = []

    while True:
        try:
            user_input = input("User > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nThank you for shopping with us! Have a great day. 👋\n")
                break

            print("\n🤖 Assistant is thinking & querying inventory...\n")
            result = agent.run(user_input, chat_history=chat_history)

            # Update context with recent turns (retain up to last 10 messages for efficiency)
            chat_history = result["messages"][-10:]

            print("Assistant >")
            print(result["output"])
            print("\n" + "-" * 72 + "\n")

        except KeyboardInterrupt:
            print("\n\nSession terminated by user. Goodbye! 👋\n")
            break
        except Exception as err:
            print(f"\n[Error during execution] {err}\n")


if __name__ == "__main__":
    main()
