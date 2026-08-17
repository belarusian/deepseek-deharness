"""Tools — plain functions in a flat dict, not a plugin registry.

In deepseek-harness the tool registry is a Cordis plugin that other plugins
register into. Here a tool is just a Python function, and the registry is a
plain dict mapping name -> function. `to_openai_tools()` renders the schema
the LLM expects. No DI, no composition.
"""
from __future__ import annotations

from typing import Any, Callable

# A tool is a plain callable: (args: dict) -> Any
Tool = Callable[[dict], Any]

# name -> Tool
Registry = dict[str, Tool]


def make_tool(name: str, description: str, parameters: dict, fn: Tool) -> dict:
    """Wrap a plain function as a tool record with its JSON schema."""
    return {
        "name": name,
        "description": description,
        "parameters": parameters,
        "fn": fn,
    }


def to_openai_tools(tools: list[dict]) -> list[dict]:
    """Render tool records into the OpenAI/DeepSeek `tools` payload shape."""
    out = []
    for t in tools:
        out.append(
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
        )
    return out


def dispatch(tools: list[dict], name: str, arguments: dict) -> Any:
    """Run a tool by name. Plain lookup + call — no registry plugin."""
    for t in tools:
        if t["name"] == name:
            return t["fn"](arguments)
    raise KeyError(f"unknown tool: {name!r}")


# --- built-in tools (the inversion of dsh's shell/fs/todo plugins) ---------

def _echo(args: dict) -> str:
    return str(args.get("text", ""))


def _add(args: dict) -> int:
    return int(args.get("a", 0)) + int(args.get("b", 0))


def builtin_tools() -> list[dict]:
    """A tiny default toolset. Plain functions, no plugin layer."""
    return [
        make_tool(
            "echo",
            "Return the given text unchanged.",
            {"type": "object", "properties": {"text": {"type": "string"}}},
            _echo,
        ),
        make_tool(
            "add",
            "Return a + b.",
            {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
            },
            _add,
        ),
    ]
