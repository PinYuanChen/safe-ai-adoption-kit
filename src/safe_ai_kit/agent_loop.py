"""Component 1: single-agent loop with tool use on the Anthropic SDK.

Stub only. The loop, tool definitions and tool-selection logic are written by
the project owner (see CLAUDE.md, Learning mode).
"""


def run_agent(question, client):
    """Answer `question` by running the agent loop against `client`.

    `client` is anything exposing `client.messages.create(...)`: a real
    `anthropic.Anthropic()` (owner-run only) or `tests/fake_client.FakeClient`.
    """
    raise NotImplementedError
