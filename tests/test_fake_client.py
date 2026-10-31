"""Tests for the test double itself, not for run_agent."""

import pytest

from fake_client import FakeClient, FakeClientExhausted, text_response, tool_use_response


def test_returns_scripted_responses_in_order():
    client = FakeClient([
        tool_use_response("lookup_order", {"order_id": "HL-10421"}, tool_id="toolu_1", text="Let me check."),
        text_response("Order HL-10421 has shipped.", input_tokens=42, output_tokens=7),
    ])

    first = client.messages.create(model="m", max_tokens=100, messages=[])
    assert first.stop_reason == "tool_use"
    assert [b.type for b in first.content] == ["text", "tool_use"]
    tool_block = first.content[1]
    assert (tool_block.id, tool_block.name, tool_block.input) == ("toolu_1", "lookup_order", {"order_id": "HL-10421"})

    second = client.messages.create(model="m", max_tokens=100, messages=[])
    assert second.stop_reason == "end_turn"
    assert second.content[0].type == "text"
    assert second.content[0].text == "Order HL-10421 has shipped."
    assert (second.usage.input_tokens, second.usage.output_tokens) == (42, 7)
    assert client.remaining == 0


def test_records_a_snapshot_of_each_call():
    client = FakeClient([text_response("a"), text_response("b")])
    messages = [{"role": "user", "content": "hi"}]

    client.messages.create(model="m", max_tokens=100, messages=messages, tools=[{"name": "t"}])
    messages.append({"role": "assistant", "content": "a"})
    client.messages.create(model="m", max_tokens=100, messages=messages)

    assert len(client.calls) == 2
    assert client.calls[0]["messages"] == [{"role": "user", "content": "hi"}]
    assert client.calls[0]["tools"] == [{"name": "t"}]
    assert len(client.calls[1]["messages"]) == 2
    assert "tools" not in client.calls[1]


def test_generates_unique_tool_ids_when_not_given():
    a = tool_use_response("t", {}).content[0].id
    b = tool_use_response("t", {}).content[0].id
    assert a != b


def test_raises_when_responses_run_out():
    client = FakeClient([text_response("only one")])
    client.messages.create(messages=[])
    with pytest.raises(FakeClientExhausted):
        client.messages.create(messages=[])
    assert len(client.calls) == 2


def test_raises_scripted_exceptions():
    client = FakeClient([RuntimeError("simulated API error"), text_response("recovered")])
    with pytest.raises(RuntimeError, match="simulated API error"):
        client.messages.create(messages=[])
    assert client.messages.create(messages=[]).content[0].text == "recovered"


def test_orders_fixture_shape(orders_data, orders):
    statuses = {o["status"] for o in orders}
    assert statuses == {"shipped", "processing", "cancelled"}
    assert 8 <= len(orders) <= 10
    known_ids = {o["order_id"] for o in orders}
    assert len(known_ids) == len(orders)
    assert orders_data["unknown_order_ids"]
    assert known_ids.isdisjoint(orders_data["unknown_order_ids"])
