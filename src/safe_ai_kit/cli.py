"""Ask the agent a question from the terminal, against the real API.

Costs money and needs a key, so run it yourself through scripts/with-secrets.sh:

    PYTHONPATH=src scripts/with-secrets.sh uv run python -m safe_ai_kit.cli "Has order HL-10421 shipped?"

The answer goes to stdout. One trace line per model call goes to stderr.
"""

import argparse
import json
import sys
from pathlib import Path

import anthropic

from safe_ai_kit.agent_loop import AgentLoopError, run_agent

ORDERS_FILE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "orders.json"


class TracingClient:
    """Wraps a client to print each model call to stderr; run_agent doesn't know it's there."""

    def __init__(self, client):
        self._client = client
        self.messages = self

    def create(self, **kwargs):
        response = self._client.messages.create(**kwargs)
        tool_calls = [f"{b.name}({json.dumps(b.input)})" for b in response.content if b.type == "tool_use"]
        usage = response.usage
        print(
            f"[model] stop_reason={response.stop_reason} tool_calls={tool_calls} "
            f"input_tokens={usage.input_tokens} output_tokens={usage.output_tokens}",
            file=sys.stderr,
        )
        return response


def main(argv=None, client=None):
    parser = argparse.ArgumentParser(description="Ask the order assistant a question.")
    parser.add_argument("question")
    args = parser.parse_args(argv)

    orders = json.loads(ORDERS_FILE.read_text())["orders"]
    traced = TracingClient(client or anthropic.Anthropic())
    try:
        print(run_agent(args.question, traced, orders))
    except (AgentLoopError, anthropic.APIError) as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
