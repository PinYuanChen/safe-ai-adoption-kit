"""Component 1: single-agent loop with tool use on the Anthropic SDK.

The loop, tool definitions and tool-selection logic are written by the project
owner (see CLAUDE.md, Learning mode). Only docstrings here are edited by Claude.
"""
from safe_ai_kit.tools import LOOKUP_ORDER_TOOL

MODEL = "claude-haiku-5-5"

def run_agent(question, client, orders):
    """Answer `question` by running the agent loop against `client`.

    Sends the question to the model with `lookup_order` available and returns
    the text of the model's reply; multiple text blocks are joined with newlines.
    Tool calls are not handled yet.

    `client` is anything exposing `client.messages.create(...)`: a real
    `anthropic.Anthropic()` (owner-run only) or `tests/fake_client.FakeClient`.
    `orders` is the order data that tools read from; it is never sent to the
    model in full.
    """
    messages = [{"role": "user", "content": question}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[LOOKUP_ORDER_TOOL],
        messages=messages,
    )
    texts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(texts)

