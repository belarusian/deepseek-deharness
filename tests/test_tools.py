"""Unit tests for tools (plain functions in a flat dict, no registry plugin)."""
from __future__ import annotations

import pytest

from deepseek_deharness.tools import (
    builtin_tools,
    dispatch,
    make_tool,
    to_openai_tools,
)


def test_builtin_tools_dispatch():
    tools = builtin_tools()
    names = {t["name"] for t in tools}
    assert {"echo", "add"} <= names
    assert dispatch(tools, "echo", {"text": "hi"}) == "hi"
    assert dispatch(tools, "add", {"a": 2, "b": 3}) == 5


def test_dispatch_unknown_tool_raises():
    with pytest.raises(KeyError):
        dispatch(builtin_tools(), "nope", {})


def test_make_tool_and_openai_shape():
    t = make_tool("f", "does f", {"type": "object"}, lambda a: a)
    rendered = to_openai_tools([t])
    assert rendered[0]["type"] == "function"
    assert rendered[0]["function"]["name"] == "f"
    assert rendered[0]["function"]["parameters"] == {"type": "object"}
