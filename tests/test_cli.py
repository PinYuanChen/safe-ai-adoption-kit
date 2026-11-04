from fake_client import FakeClient, text_response, tool_use_response
from safe_ai_kit.cli import main


def test_prints_answer_to_stdout_and_trace_to_stderr(capsys):
    client = FakeClient([
        tool_use_response("lookup_order", {"order_id": "HL-10421"}, input_tokens=42, output_tokens=7),
        text_response("Order HL-10421 has shipped."),
    ])

    exit_code = main(["Has order HL-10421 shipped?"], client=client)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "Order HL-10421 has shipped.\n"
    assert 'lookup_order({"order_id": "HL-10421"})' in captured.err
    assert "input_tokens=42 output_tokens=7" in captured.err
    assert client.calls[0]["messages"][0]["content"] == "Has order HL-10421 shipped?"


def test_reads_synthetic_orders_so_the_tool_finds_a_real_fixture_order(capsys):
    client = FakeClient([
        tool_use_response("lookup_order", {"order_id": "HL-10436"}),
        text_response("done"),
    ])

    main(["Why was HL-10436 cancelled?"], client=client)

    tool_result = client.calls[1]["messages"][2]["content"][0]
    assert "out_of_stock" in tool_result["content"]


def test_agent_failure_exits_nonzero_with_nothing_on_stdout(capsys):
    client = FakeClient([text_response("cut off", stop_reason="max_tokens")])

    exit_code = main(["Has order HL-10421 shipped?"], client=client)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "AgentLoopError" in captured.err
