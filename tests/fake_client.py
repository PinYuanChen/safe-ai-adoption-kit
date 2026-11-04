"""A scripted stand-in for `anthropic.Anthropic` used by every test.

Queue responses up front; each `client.messages.create(**kwargs)` call returns
the next one and records a deep copy of its kwargs in `client.calls`.
Response objects expose the same attributes the SDK's `Message` does:
`.stop_reason`, `.content` (blocks with `.type`), and `.usage`.
"""

import copy
import itertools
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class TextBlock:
    text: str
    type: Literal["text"] = "text"


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: Literal["tool_use"] = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class FakeMessage:
    content: list[TextBlock | ToolUseBlock]
    stop_reason: str
    usage: Usage = field(default_factory=Usage)
    id: str = "msg_fake"
    model: str = "fake-model"
    role: Literal["assistant"] = "assistant"
    type: Literal["message"] = "message"


_tool_ids = itertools.count(1)


def text_response(text, *, input_tokens=10, output_tokens=5, stop_reason="end_turn"):
    """A final answer: one text block, stop_reason "end_turn" by default."""
    return FakeMessage(
        content=[TextBlock(text=text)],
        stop_reason=stop_reason,
        usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def tool_use_response(name, tool_input, *, tool_id=None, text=None, input_tokens=10, output_tokens=5):
    """A tool call, optionally preceded by a text block, stop_reason "tool_use"."""
    content = [TextBlock(text=text)] if text is not None else []
    content.append(ToolUseBlock(id=tool_id or f"toolu_fake_{next(_tool_ids):03d}", name=name, input=tool_input))
    return FakeMessage(
        content=content,
        stop_reason="tool_use",
        usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
    )


class FakeClientExhausted(AssertionError):
    """Raised when create() is called after every scripted response was used.

    Usually means the code under test looped more times than the test expected.
    """


class _FakeMessages:
    def __init__(self, client):
        self._client = client

    def create(self, **kwargs):
        client = self._client
        # Deep copy: the caller typically keeps appending to the same messages list.
        client.calls.append(copy.deepcopy(kwargs))
        if not client._responses:
            raise FakeClientExhausted(f"create() call #{len(client.calls)} has no scripted response left")
        response = client._responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class FakeClient:
    """Pass a list of FakeMessage (or exceptions to raise, simulating API errors)."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = _FakeMessages(self)

    @property
    def remaining(self):
        return len(self._responses)
