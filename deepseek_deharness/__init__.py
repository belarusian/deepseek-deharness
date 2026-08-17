"""deepseek-deharness: a monolithic agent harness.

One flat program: loop + tools + session + llm-adapter as plain functions.
No plugin layer, no DI container. Organized by the four algebra:
  - inner spoke: work + trajectory
  - outer spoke: append-only log reconciliation

This is the exact inversion of deepseek-harness (dsh) + cordis, where the
agent is 40+ Cordis plugins composed by profiles/bundles/patches.
"""
from __future__ import annotations

from .harness import run_harness
from .llm_adapter import call_llm
from .log import Log
from .replay import reconstruct_session, replay
from .run import inner_spoke, outer_spoke, run
from .session import Session
from .tools import builtin_tools, dispatch, make_tool, to_openai_tools

__version__ = "0.1.0"

__all__ = [
    "Log",
    "Session",
    "__version__",
    "builtin_tools",
    "call_llm",
    "dispatch",
    "inner_spoke",
    "make_tool",
    "outer_spoke",
    "reconstruct_session",
    "replay",
    "run",
    "run_harness",
    "to_openai_tools",
]
