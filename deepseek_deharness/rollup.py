"""Multi-run rollup — the aggregate view plus per-log size detail in one view.

Cycle 15 made N finished runs *rollable to a batch with outcome* (aggregate.
aggregate_runs): how many ran, is every one healthy, are they all the same run,
what did each finally answer, and how much work did the batch do? This module
adds the per-log *size* detail that aggregate deliberately left out — each log's
estimated token count — so a batch of runs can be checked for health/identity/
outcome AND size in one call.

One plain function, stdlib only, no plugin layer, no DI:

    rollup_runs(paths) -> dict
        A read-only multi-run report that composes the existing aggregate view
        (aggregate.aggregate_runs) with per-log size detail (audit.audit_log).
        Returns {runs, all_healthy, total_entries, max_estimated_tokens,
        identical_all, final_responses, tool_calls_total, estimated_tokens_per_log}.
        Reuses both plain functions; does not re-implement them. Never mutates
        any log file.
"""
from __future__ import annotations

from pathlib import Path

from .aggregate import aggregate_runs
from .audit import audit_log


def rollup_runs(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run report with per-log size detail.

    Composes the existing aggregate view with per-log size detail. Keys:
      runs                 : int — from aggregate.aggregate_runs.
      all_healthy          : bool — from aggregate.aggregate_runs.
      total_entries        : int — from aggregate.aggregate_runs.
      max_estimated_tokens : int — from aggregate.aggregate_runs.
      identical_all        : bool — from aggregate.aggregate_runs.
      final_responses      : list[str | None] — from aggregate.aggregate_runs.
      tool_calls_total     : int — from aggregate.aggregate_runs.
      estimated_tokens_per_log : list[int] — [audit.audit_log(p)["estimated_tokens"]
                             for p in paths], aligned with the input order (one per log).

    The seven keys are taken directly from aggregate.aggregate_runs(paths); they
    are not re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = aggregate_runs(paths)

    estimated_tokens_per_log: list[int] = [audit_log(p)["estimated_tokens"] for p in paths]

    return {
        "runs": report["runs"],
        "all_healthy": report["all_healthy"],
        "total_entries": report["total_entries"],
        "max_estimated_tokens": report["max_estimated_tokens"],
        "identical_all": report["identical_all"],
        "final_responses": report["final_responses"],
        "tool_calls_total": report["tool_calls_total"],
        "estimated_tokens_per_log": estimated_tokens_per_log,
    }
