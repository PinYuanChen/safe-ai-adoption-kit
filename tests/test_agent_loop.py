from fake_client import FakeClient, text_response
from safe_ai_kit.agent_loop import run_agent
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


