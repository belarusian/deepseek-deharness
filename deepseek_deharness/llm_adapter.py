"""LLM adapter — a plain function, not a plugin.

In deepseek-harness the model adapter is one of 40+ Cordis plugins composed
into a shared context. Here it is a single function: `call_llm`. No class, no
DI container, no profile/bundle/patch. The only seam is `transport`, a plain
callable you may swap in tests.
"""
from __future__ import annotations

from typing import Any, Callable

# transport(payload: dict) -> dict  (the only injectable seam)
Transport = Callable[[dict], dict]


def _default_transport(payload: dict) -> dict:
    """Real HTTP transport. Kept tiny and swappable; tests never hit it."""
    import json
    import os
    import urllib.request

    url = os.environ.get("DEH_LLM_URL", "https://api.deepseek.com/v1/chat/completions")
    key = os.environ.get("DEH_LLM_KEY", "")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def call_llm(
    messages: list[dict],
    model: str,
    *,
    transport: Transport = _default_transport,
    tools: list[dict] | None = None,
    **kwargs: Any,
) -> dict:
    """Call the LLM and return a structured response.

    Returns a dict with keys:
      content    : str | None
      tool_calls : list[dict]   (each: id, name, arguments)
      usage      : dict
    """
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
    payload.update(kwargs)

    raw = transport(payload)
    choice = (raw.get("choices") or [{}])[0]
    message = choice.get("message") or {}

    tool_calls = []
    for tc in message.get("tool_calls") or []:
        fn = tc.get("function") or {}
        args = fn.get("arguments")
        if isinstance(args, str):
            try:
                import json

                args = json.loads(args)
            except (ValueError, TypeError):
                args = {"raw": args}
        tool_calls.append(
            {"id": tc.get("id"), "name": fn.get("name"), "arguments": args or {}}
        )

    return {
        "content": message.get("content"),
        "tool_calls": tool_calls,
        "usage": raw.get("usage") or {},
    }
