"""Log health audit — one read-only report composing the per-concern functions.

Cycle 4 made the source of truth *auditable* (verify), Cycle 5 *inspectable*
(summarize), and Cycle 7 *budgetable* (estimate_tokens). This module composes
those three plain functions into a single health view so a finished run can be
checked at a glance: is it healthy, what does it end with, how many tool calls
did it make, and roughly how big is it?

One plain function, stdlib only, no plugin layer, no DI:

    audit_log(log_path) -> dict
        A read-only health report for an append-only log. Returns
        {entries, healthy, violations, final_response, tool_calls,
        estimated_tokens}. Reuses repair.verify_log, inspect.summarize_log, and
        compact.estimate_tokens (does not re-implement them). Never mutates the
        log file.
"""
from __future__ import annotations

from pathlib import Path

from .compact import estimate_tokens
from .inspect import summarize_log
from .repair import verify_log


def audit_log(log_path: str | Path) -> dict:
    """Return a single read-only health report for an append-only log.

    Composes the existing per-concern functions into one view. Keys:
      entries          : int — number of log lines (from summarize_log).
      healthy          : bool — True iff verify_log(log_path) == [].
      violations       : list[dict] — raw violation records from verify_log.
      final_response   : str | None — last assistant content (from summarize_log).
      tool_calls       : int — number of tool calls seen across any entry's step.
      estimated_tokens : int — cheap token estimate (from compact.estimate_tokens).

    This function never writes to or mutates the log file.
    """
    violations = verify_log(log_path)
    summary = summarize_log(log_path)

    return {
        "entries": summary["entries"],
        "healthy": not violations,
        "violations": violations,
        "final_response": summary["final_response"],
        "tool_calls": len(summary["tool_calls"]),
        "estimated_tokens": estimate_tokens(log_path),
    }
