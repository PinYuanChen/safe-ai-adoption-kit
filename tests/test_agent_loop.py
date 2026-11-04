import json

import pytest

from fake_client import FakeClient, FakeMessage, TextBlock, text_response, tool_use_response, ToolUseBlock
from safe_ai_kit.agent_loop import run_agent, AgentLoopError, MAX_TURNS, run_tool
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


def test_raises_on_unexpected_stop_reason_max_tokens(orders):
    client = FakeClient([
        text_response("Order HL-10421 shipped on", stop_reason="max_tokens"),
    ])

    with pytest.raises(AgentLoopError, match="stop_reason: max_tokens"):

        run_agent("Has order HL-10421 shipped?", client, orders)

    assert len(client.calls) == 1


def test_raises_on_unexpected_stop_reason_refusal(orders):
    client = FakeClient([
        text_response("Order HL-10421 shipped on", stop_reason="refusal"),
    ])

    with pytest.raises(AgentLoopError, match="stop_reason: refusal"):
        run_agent("Has order HL-10421 shipped?", client, orders)

    assert len(client.calls) == 1


def test_reports_unknown_tool_back_to_the_model(orders):
    reply = "Sorry, I cannot cancel order HL-10425 because the tool does not exist."
    client = FakeClient([
        tool_use_response("cancel_order", {"order_id": "HL-10425"}, tool_id="toolu_unknown"),
        text_response(reply),
    ])

    answer = run_agent("Please cancel order HL-10425.", client, orders)

    assert answer == reply
    assert len(client.calls) == 2

    tool_result = client.calls[1]["messages"][2]["content"][0]
    assert tool_result["tool_use_id"] == "toolu_unknown"
    assert tool_result["is_error"] is True
    assert "cancel_order" in tool_result["content"]


def test_lookup_order_missing_order_id(orders):
    block = ToolUseBlock(id="toolu_1", name="lookup_order", input={})

    result = run_tool(block, orders)

    assert result["is_error"] is True
    assert result["tool_use_id"] == "toolu_1"
    assert "order_id" in result["content"]


def test_lookup_order_wrong_type(orders):
    block = ToolUseBlock(id="toolu_2", name="lookup_order", input={"order_id": 10421})

    result = run_tool(block, orders)

    assert result["is_error"] is True
    assert result["tool_use_id"] == "toolu_2"
    assert "string" in result["content"]


def test_joins_multiple_text_blocks_with_newlines(orders):
    client = FakeClient([
        FakeMessage(
            content=[
                TextBlock(text="Order HL-10421 has shipped."),
                TextBlock(text="It should arrive by 2026-09-30."),
            ],
            stop_reason="end_turn",
        ),
    ])

    answer = run_agent("Has order HL-10421 shipped?", client, orders)

    assert answer == "Order HL-10421 has shipped.\nIt should arrive by 2026-09-30."


def test_text_before_a_tool_call_is_kept_in_history_but_not_in_the_answer(orders):
    reply = "Yes, order HL-10421 shipped on 2026-09-09."
    client = FakeClient([
        tool_use_response(
            "lookup_order", {"order_id": "HL-10421"},
            tool_id="toolu_pre", text="Let me check that order.",
        ),
        text_response(reply),
    ])

    answer = run_agent("Has order HL-10421 shipped?", client, orders)

    assert answer == reply
    assert "Let me check" not in answer

    assistant_turn = client.calls[1]["messages"][1]
    assert assistant_turn["role"] == "assistant"
    assert [block.type for block in assistant_turn["content"]] == ["text", "tool_use"]
    assert assistant_turn["content"][0].text == "Let me check that order."


def test_raises_when_end_turn_has_no_text(orders):
    client = FakeClient([FakeMessage(content=[], stop_reason="end_turn")])

    with pytest.raises(AgentLoopError, match="no text"):
        run_agent("Has order HL-10421 shipped?", client, orders)

    assert len(client.calls) == 1


def test_raises_when_end_turn_text_is_only_whitespace(orders):
    client = FakeClient([text_response("  \n ")])

    with pytest.raises(AgentLoopError, match="no text"):
        run_agent("Has order HL-10421 shipped?", client, orders)


def test_unknown_tool_without_order_id(orders):
    block = ToolUseBlock(id="toolu_3", name="cancel_order", input={})
    result = run_tool(block, orders)
    assert result["is_error"] is True
    assert "cancel_order" in result["content"]
    assert "lookup_order" not in result["content"]


def test_tool_crash_is_reported_to_the_model():
    block = ToolUseBlock(id="toolu_crash", name="lookup_order", input={"order_id": "HL-10421"})

    result = run_tool(block, [{"id": "HL-10421"}])

    assert result["is_error"] is True
    assert result["tool_use_id"] == "toolu_crash"


class BrokenStore:
    def __iter__(self):
        raise RuntimeError("SECRET-INTERNAL-DETAIL")


def test_tool_crash_does_not_leak_internal_details():
    block = ToolUseBlock(id="toolu_leak", name="lookup_order", input={"order_id": "HL-10421"})

    result = run_tool(block, BrokenStore())

    assert result["is_error"] is True
    assert "SECRET-INTERNAL-DETAIL" not in result["content"]