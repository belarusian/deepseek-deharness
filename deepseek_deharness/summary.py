"""Multi-run summary — the rollout view plus per-log entry count in one view.

Cycle 20 made N finished runs *rollable to a rollout with per-log final-response
length* (rollout.batch_rollout): how many ran, is every one healthy, are they all
the same run, what did each finally answer, how much work did the batch do, how big
is each log in estimated tokens, which individual logs are healthy, which individual
logs actually produced a non-None final assistant response, how many tool calls each
individual log made, and how long (in characters) each log's final assistant response
is. This module adds the per-log *entry count* detail that rollout deliberately left
out — how many entries (log lines) each individual log has — so a batch of runs can
be checked for health/identity/outcome/size/health/presence/tool-calls-per-log/
final-response-len-per-log AND per-log entry count in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_summary(paths) -> dict
        A read-only multi-run summary that composes the existing rollout view
        (rollout.batch_rollout) with per-log entry-count detail. Returns
        {runs, all_healthy, total_entries, max_estimated_tokens, identical_all,
        final_responses, tool_calls_total, estimated_tokens_per_log, healthy_per_log,
        has_final_response_per_log, tool_calls_per_log, final_response_len_per_log,
        entries_per_log}. Reuses batch_rollout and inspect.summarize_log; does not
        re-implement either. Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .inspect import summarize_log
from .rollout import batch_rollout


def batch_summary(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run summary with per-log entry count.

    Composes the existing rollout view with per-log entry-count detail. Keys:
      runs                 : int — from rollout.batch_rollout.
      all_healthy          : bool — from rollout.batch_rollout.
      total_entries        : int — from rollout.batch_rollout.
      max_estimated_tokens : int — from rollout.batch_rollout.
      identical_all        : bool — from rollout.batch_rollout.
      final_responses      : list[str | None] — from rollout.batch_rollout.
      tool_calls_total     : int — from rollout.batch_rollout.
      estimated_tokens_per_log : list[int] — from rollout.batch_rollout.
      healthy_per_log      : list[bool] — from rollout.batch_rollout.
      has_final_response_per_log : list[bool] — from rollout.batch_rollout.
      tool_calls_per_log   : list[int] — from rollout.batch_rollout.
      final_response_len_per_log : list[int] — from rollout.batch_rollout.
      entries_per_log      : list[int] — [summarize_log(p)["entries"] for p in paths],
                             aligned with the input order (one per log; that log's
                             entry count).

    The twelve keys are taken directly from rollout.batch_rollout(paths); they are
    not re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = batch_rollout(paths)

    entries_per_log: list[int] = [summarize_log(p)["entries"] for p in paths]

    return {
        "runs": report["runs"],
        "all_healthy": report["all_healthy"],
        "total_entries": report["total_entries"],
        "max_estimated_tokens": report["max_estimated_tokens"],
        "identical_all": report["identical_all"],
        "final_responses": report["final_responses"],
        "tool_calls_total": report["tool_calls_total"],
        "estimated_tokens_per_log": report["estimated_tokens_per_log"],
        "healthy_per_log": report["healthy_per_log"],
        "has_final_response_per_log": report["has_final_response_per_log"],
        "tool_calls_per_log": report["tool_calls_per_log"],
        "final_response_len_per_log": report["final_response_len_per_log"],
        "entries_per_log": entries_per_log,
    }
