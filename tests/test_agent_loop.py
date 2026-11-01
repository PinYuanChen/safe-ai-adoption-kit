import json

import pytest

from fake_client import FakeClient, text_response, tool_use_response
from safe_ai_kit.agent_loop import run_agent, AgentLoopError, MAX_TURNS
from safe_ai_kit.tools import LOOKUP_ORDER_TOOL


def test_returns_text_when_model_answers_directly(orders):
    question = "Hi, what can you help me with?"
    reply = "I can look up the status of your Harbor Lantern orders. What's your order ID?"
    client = FakeClient([text_response(reply)])
    answer = run_agent(question, client, orders)
    assert answer == reply
    assert len(client.calls) == 1
    assert client.calls[0]["messages"] == [{"role": "user", "content": question}]
    assert client.calls[0]["tools"] == [LOOKUP_ORDER_TOOL]


def test_runs_a_tool_and_returns_the_final_answer(orders):
    question = "Has order HL-10421 shipped?"
    reply = "Yes, order HL-10421 shipped on 2026-09-09 via Bluegate Freight (tracking BGF-000-417-221). It should arrive by 2026-09-30."
    client = FakeClient([
        tool_use_response("lookup_order", {"order_id": "HL-10421"}, tool_id="toolu_test_1"),
        text_response(reply),
    ])

    answer = run_agent(question, client, orders)

    assert answer == reply
    assert len(client.calls) == 2

    second_messages = client.calls[1]["messages"]
    assert [m["role"] for m in second_messages] == ["user", "assistant", "user"]

    tool_result = second_messages[2]["content"][0]
    assert tool_result["type"] == "tool_result"
    assert tool_result["tool_use_id"] == "toolu_test_1"
    assert json.loads(tool_result["content"])["status"] == "shipped"

    assert client.calls[1]["tools"] == [LOOKUP_ORDER_TOOL]


def test_raises_when_model_keeps_calling_tools(orders):
    client = FakeClient([
        tool_use_response("lookup_order", {"order_id": "HL-10421"})
        for _ in range(MAX_TURNS + 3)
    ])

    with pytest.raises(AgentLoopError, match="max turns"):
        run_agent("Has order HL-10421 shipped?", client, orders)

    assert len(client.calls) == MAX_TURNS


def test_raises_on_unexpected_stop_reason(orders):
    client = FakeClient([
        text_response("Order HL-10421 shipped on", stop_reason="max_tokens"),
    ])

    with pytest.raises(AgentLoopError, match="unexpected stop_reason: max_tokens"):
        run_agent("Has order HL-10421 shipped?", client, orders)

    assert len(client.calls) == 1