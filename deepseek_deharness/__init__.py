"""deepseek-deharness: a monolithic agent harness.

One flat program: loop + tools + session + llm-adapter as plain functions.
No plugin layer, no DI container. Organized by the four algebra:
  - inner spoke: work + trajectory
  - outer spoke: append-only log reconciliation

This is the exact inversion of deepseek-harness (dsh) + cordis, where the
agent is 40+ Cordis plugins composed by profiles/bundles/patches.
"""
from __future__ import annotations

from .aggregate import aggregate_runs
from .audit import audit_log
from .budget import fits_budget, plan_compaction
from .compact import compact_log, estimate_tokens
from .compare import compare_logs
from .harness import run_harness
from .inspect import diff_logs, summarize_log
from .llm_adapter import call_llm
from .log import Log
from .repair import repair_log, verify_log
from .replay import reconstruct_session, replay
from .rollup import rollup_runs
from .run import inner_spoke, outer_spoke, run
from .session import Session
from .summarize import summarize_runs
from .tools import builtin_tools, dispatch, make_tool, to_openai_tools
from .trace import extract_trajectory, trajectory_stats

__version__ = "0.1.0"

__all__ = [
    "Log",
    "Session",
    "__version__",
    "aggregate_runs",
    "audit_log",
    "builtin_tools",
    "call_llm",
    "compact_log",
    "compare_logs",
    "diff_logs",
    "dispatch",
    "estimate_tokens",
    "extract_trajectory",
    "fits_budget",
    "inner_spoke",
    "make_tool",
    "outer_spoke",
    "plan_compaction",
    "reconstruct_session",
    "repair_log",
    "replay",
    "rollup_runs",
    "run",
    "run_harness",
    "summarize_log",
    "summarize_runs",
    "to_openai_tools",
    "trajectory_stats",
    "verify_log",
]
