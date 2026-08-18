"""Multi-run report — the batch rollup plus per-log detail in one view.

Cycle 14 made N finished runs *rollable to a batch* (summarize.summarize_runs):
how many ran, is every one healthy, how big is the biggest, are they all the
same run? This module adds the per-log *detail* that rollup deliberately left
out — each log's final response and its tool-call count — so a batch of runs
can be checked for both health/identity AND outcome in one call.

One plain function, stdlib only, no plugin layer, no DI:

    aggregate_runs(paths) -> dict
        A read-only multi-run report that composes the existing batch rollup
        (summarize.summarize_runs) with per-log detail (inspect.summarize_log).
        Returns {runs, all_healthy, total_entries, max_estimated_tokens,
        identical_all, final_responses, tool_calls_total}. Reuses both plain
        functions; does not re-implement them. Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .inspect import summarize_log
from .summarize import summarize_runs


def aggregate_runs(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run report with per-log detail.

    Composes the existing batch rollup with per-log detail. Keys:
      runs                 : int — from summarize.summarize_runs.
      all_healthy          : bool — from summarize.summarize_runs.
      total_entries        : int — from summarize.summarize_runs.
      max_estimated_tokens : int — from summarize.summarize_runs.
      identical_all        : bool — from summarize.summarize_runs.
      final_responses      : list[str | None] — [summarize_log(p)["final_response"]
                             for p in paths], aligned with the input order (one per
                             log; None when a log has no assistant content).
      tool_calls_total     : int — sum over each log's summarize_log(p) of
                             len(tool_calls).

    The five rollup keys are taken directly from summarize.summarize_runs(paths);
    they are not re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    rollup = summarize_runs(paths)

    details = [summarize_log(p) for p in paths]
    final_responses: list[str | None] = [d["final_response"] for d in details]
    tool_calls_total = sum(len(d["tool_calls"]) for d in details)

    return {
        "runs": rollup["runs"],
        "all_healthy": rollup["all_healthy"],
        "total_entries": rollup["total_entries"],
        "max_estimated_tokens": rollup["max_estimated_tokens"],
        "identical_all": rollup["identical_all"],
        "final_responses": final_responses,
        "tool_calls_total": tool_calls_total,
    }
