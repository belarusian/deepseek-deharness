"""Multi-run batch report — the rollup view plus per-log health detail in one view.

Cycle 16 made N finished runs *rollable to a batch with size* (rollup.rollup_runs):
how many ran, is every one healthy, are they all the same run, what did each finally
answer, how much work did the batch do, and how big is each log in estimated tokens.
This module adds the per-log *health* detail that rollup deliberately left out — each
log's healthy flag — so a batch of runs can be checked for health/identity/outcome/size
AND per-log health in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_report(paths) -> dict
        A read-only multi-run report that composes the existing rollup view
        (rollup.rollup_runs) with per-log health detail (audit.audit_log).
        Returns {runs, all_healthy, total_entries, max_estimated_tokens,
        identical_all, final_responses, tool_calls_total, estimated_tokens_per_log,
        healthy_per_log}. Reuses both plain functions; does not re-implement them.
        Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .audit import audit_log
from .rollup import rollup_runs


def batch_report(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run report with per-log health detail.

    Composes the existing rollup view with per-log health detail. Keys:
      runs                 : int — from rollup.rollup_runs.
      all_healthy          : bool — from rollup.rollup_runs.
      total_entries        : int — from rollup.rollup_runs.
      max_estimated_tokens : int — from rollup.rollup_runs.
      identical_all        : bool — from rollup.rollup_runs.
      final_responses      : list[str | None] — from rollup.rollup_runs.
      tool_calls_total     : int — from rollup.rollup_runs.
      estimated_tokens_per_log : list[int] — from rollup.rollup_runs.
      healthy_per_log      : list[bool] — [audit.audit_log(p)["healthy"] for p in paths],
                             aligned with the input order (one per log).

    The eight keys are taken directly from rollup.rollup_runs(paths); they are not
    re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = rollup_runs(paths)

    healthy_per_log: list[bool] = [audit_log(p)["healthy"] for p in paths]

    return {
        "runs": report["runs"],
        "all_healthy": report["all_healthy"],
        "total_entries": report["total_entries"],
        "max_estimated_tokens": report["max_estimated_tokens"],
        "identical_all": report["identical_all"],
        "final_responses": report["final_responses"],
        "tool_calls_total": report["tool_calls_total"],
        "estimated_tokens_per_log": report["estimated_tokens_per_log"],
        "healthy_per_log": healthy_per_log,
    }
