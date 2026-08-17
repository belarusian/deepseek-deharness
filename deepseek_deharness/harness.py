"""The harness — one flat function, not a composed plugin graph.

deepseek-harness exposes `DeepSeekHarness(...)` as a context manager that
boots a Cordis plugin graph (40+ packages) from a profile/bundle/patch. The
inversion is a single plain function: `run_harness`. It wires the four
algebra (run.py) to a default toolset and returns the result. No DI, no
composition layer.
"""
from __future__ import annotations

from typing import Any, Callable

from .run import run
from .tools import builtin_tools


def run_harness(
    goal: str,
    *,
    model: str = "deepseek-v4-flash",
    system: str | None = None,
    tools: list[dict] | None = None,
    log_path: str = ".deepseek-deharness/log.jsonl",
    max_turns: int = 8,
    transport: Callable | None = None,
) -> dict:
    """Run the monolithic agent harness on a goal.

    This is the whole program's entry point. It is a plain function that
    calls the four algebra directly — the inversion of dsh's plugin boot.
    """
    if tools is None:
        tools = builtin_tools()
    return run(
        goal,
        model=model,
        system=system,
        tools=tools,
        log_path=log_path,
        max_turns=max_turns,
        transport=transport,
    )
