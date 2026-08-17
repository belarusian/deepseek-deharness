"""Unit tests for the LLM adapter (plain function, mocked transport)."""
from __future__ import annotations

from deepseek_deharness.llm_adapter import call_llm


def _fake_transport(payload):
    # Echo back a structured completion: one tool call, then content.
    assert payload["model"]
    assert isinstance(payload["messages"], list)
    return {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "add",
                                "arguments": '{"a": 2, "b": 3}',
                            },
                        }
                    ],
                }
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7},
    }


def test_call_llm_parses_tool_calls_and_usage():
    resp = call_llm(
        [{"role": "user", "content": "hi"}],
        "deepseek-v4-flash",
        transport=_fake_transport,
    )
    assert resp["content"] is None
    assert len(resp["tool_calls"]) == 1
    tc = resp["tool_calls"][0]
    assert tc["id"] == "call_1"
    assert tc["name"] == "add"
    assert tc["arguments"] == {"a": 2, "b": 3}  # JSON string decoded
    assert resp["usage"]["completion_tokens"] == 7


def test_call_llm_content_only():
    def t(payload):
        return {"choices": [{"message": {"content": "hello"}}], "usage": {}}

    resp = call_llm([{"role": "user", "content": "hi"}], "m", transport=t)
    assert resp["content"] == "hello"
    assert resp["tool_calls"] == []
    assert resp["usage"] == {}


def test_call_llm_passes_tools_and_kwargs():
    seen = {}

    def t(payload):
        seen.update(payload)
        return {"choices": [{"message": {"content": "ok"}}]}

    call_llm(
        [{"role": "user", "content": "x"}],
        "m",
        transport=t,
        tools=[{"type": "function", "function": {"name": "add"}}],
        temperature=0.2,
    )
    assert seen["tools"][0]["function"]["name"] == "add"
    assert seen["temperature"] == 0.2
