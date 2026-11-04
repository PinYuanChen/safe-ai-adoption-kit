"""Component 1: single-agent loop with tool use on the Anthropic SDK.

The loop, tool definitions and tool-selection logic are written by the project
owner (see CLAUDE.md, Learning mode). Only docstrings here are edited by Claude.
"""

import json
import sys

from safe_ai_kit.tools import LOOKUP_ORDER_TOOL, lookup_order

MODEL = "claude-haiku-5-5"
MAX_TURNS = 5


class AgentLoopError(Exception):
    """Raised when the agent loop cannot finish normally."""


def run_agent(question, client, orders):
    """Answer `question` by running the agent loop against `client`.

    Sends the question to the model with `lookup_order` available. Each time the
    model asks for `lookup_order`, runs it and sends the result back, until the
    model ends its turn; then returns the reply's text blocks joined with
    newlines. Raises AgentLoopError if the model has not finished within
    MAX_TURNS calls, ends its turn with no text, or stops for an unexpected
    reason.

    `client` is anything exposing `client.messages.create(...)`: a real
    `anthropic.Anthropic()` (owner-run only) or `tests/fake_client.FakeClient`.
    `orders` is the order data that tools read from; it is never sent to the
    model in full.
    """
    messages = [{"role": "user", "content": question}]
    for turn in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[LOOKUP_ORDER_TOOL],
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            texts = [block.text for block in response.content if block.type == "text"]
            answer = "\n".join(texts)
            if not answer.strip():
                raise AgentLoopError(f"end_turn with no text on turn {turn + 1}")
            return answer
        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_results.append(run_tool(block, orders))
            messages.append({"role": "user", "content": tool_results})
        else:
            raise AgentLoopError(f"stop_reason: {response.stop_reason} on turn {turn + 1}")
    raise AgentLoopError(f"max turns {MAX_TURNS} reached")


def run_tool(block, orders) -> dict:
    if block.name == "lookup_order":
        order_id = block.input.get("order_id")
        if order_id is None:
            return {
                "type": "tool_result",
                "is_error": True,
                "tool_use_id": block.id,
                "content": "lookup_order is missing the required 'order_id' argument.",
            }
        if not isinstance(order_id, str):
            return {
                "type": "tool_result",
                "is_error": True,
                "tool_use_id": block.id,
                "content": f"lookup_order needs 'order_id' as a string, got {type(order_id).__name__}.",
            }
        try:
            result = lookup_order(order_id, orders)
            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            }
        except Exception as e:
            print(f"lookup_order failed: {type(e).__name__}: {e}", file=sys.stderr)
            return {
                "type": "tool_result",
                "is_error": True,
                "tool_use_id": block.id,
                "content": "lookup_order failed due to an internal error. Tell the user the order system is temporarily unavailable and to try again later.",
            }
    else:
        return {
            "type": "tool_result",
            "is_error": True,
            "tool_use_id": block.id,
            "content": f"Tool {block.name} is not available in this agent loop.",
        }