"""Integration test for the real HTTP transport path (mocked at urllib level).

Cycle 1's unit tests swap in a fake `transport` callable. This test goes one
level deeper: it drives `call_llm` with the *default* transport
(`_default_transport`, which uses `urllib.request`) and mocks only
`urllib.request.urlopen`. That proves the adapter works end-to-end — correct
URL, headers, JSON body shape, and response parsing into
`{content, tool_calls, usage}` — without ever hitting a real LLM.

Stdlib only (urllib, json). No new dependencies.
"""
from __future__ import annotations

import json
from unittest import mock

from deepseek_deharness.llm_adapter import _default_transport, call_llm


def _fake_urlopen(req):
    """Stand in for urllib.request.urlopen; return a readable response body."""
    raw = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_http",
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
        "usage": {"prompt_tokens": 11, "completion_tokens": 4},
    }
    body = json.dumps(raw).encode("utf-8")
    resp = mock.Mock()
    resp.read.return_value = body
    # Support `with urllib.request.urlopen(req) as resp:` (context manager).
    resp.__enter__ = mock.Mock(return_value=resp)
    resp.__exit__ = mock.Mock(return_value=False)
    return resp


def test_default_transport_posts_correct_request_and_parses(monkeypatch):
    """Drive call_llm through the real urllib path with urlopen mocked."""
    captured: dict = {}

    def fake_urlopen(req):
        # Capture what the transport actually sent over the wire.
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _fake_urlopen(req)

    monkeypatch.setenv("DEH_LLM_URL", "https://example.test/v1/chat/completions")
    monkeypatch.setenv("DEH_LLM_KEY", "sk-test-key")

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        resp = call_llm(
            [{"role": "user", "content": "add 2 and 3"}],
            "deepseek-v4-flash",
            tools=[{"type": "function", "function": {"name": "add"}}],
        )

    # --- request shape (URL, method, headers, JSON body) -------------------
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["method"] == "POST"
    assert captured["headers"]["content-type"] == "application/json"
    assert captured["headers"]["authorization"] == "Bearer sk-test-key"

    body = captured["body"]
    assert body["model"] == "deepseek-v4-flash"
    assert body["messages"] == [{"role": "user", "content": "add 2 and 3"}]
    # tools were rendered into the OpenAI/DeepSeek payload shape.
    assert body["tools"][0]["type"] == "function"
    assert body["tools"][0]["function"]["name"] == "add"

    # --- response parsing into {content, tool_calls, usage} -----------------
    assert resp["content"] is None
    assert len(resp["tool_calls"]) == 1
    tc = resp["tool_calls"][0]
    assert tc["id"] == "call_http"
    assert tc["name"] == "add"
    assert tc["arguments"] == {"a": 2, "b": 3}  # JSON string decoded to dict
    assert resp["usage"] == {"prompt_tokens": 11, "completion_tokens": 4}


def test_default_transport_content_only(monkeypatch):
    """A content-only completion parses cleanly through the urllib path."""

    def fake_urlopen(req):
        raw = {"choices": [{"message": {"content": "hello"}}], "usage": {}}
        body = json.dumps(raw).encode("utf-8")
        resp = mock.Mock()
        resp.read.return_value = body
        resp.__enter__ = mock.Mock(return_value=resp)
        resp.__exit__ = mock.Mock(return_value=False)
        return resp

    monkeypatch.setenv("DEH_LLM_URL", "https://example.test/v1/chat/completions")
    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        resp = call_llm([{"role": "user", "content": "hi"}], "m")

    assert resp["content"] == "hello"
    assert resp["tool_calls"] == []
    assert resp["usage"] == {}


def test_default_transport_is_the_real_urllib_path():
    """Sanity: the default transport is a plain function using urllib.request."""
    import inspect

    src = inspect.getsource(_default_transport)
    assert "urllib.request" in src
    # It is a plain function, not a class/plugin.
    assert inspect.isfunction(_default_transport)


def test_default_transport_reads_env_defaults(monkeypatch):
    """With no env vars set it falls back to the DeepSeek endpoint."""
    monkeypatch.delenv("DEH_LLM_URL", raising=False)
    monkeypatch.delenv("DEH_LLM_KEY", raising=False)

    captured: dict = {}

    def fake_urlopen(req):
        captured["url"] = req.full_url
        captured["auth"] = {k.lower(): v for k, v in req.header_items()}["authorization"]
        resp = mock.Mock()
        resp.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "ok"}}], "usage": {}}
        ).encode("utf-8")
        resp.__enter__ = mock.Mock(return_value=resp)
        resp.__exit__ = mock.Mock(return_value=False)
        return resp

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        call_llm([{"role": "user", "content": "hi"}], "m")

    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["auth"] == "Bearer "  # empty key -> empty bearer token
