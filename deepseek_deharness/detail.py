"""Multi-run detail — the summary view plus per-log message count in one view.

Cycle 21 made N finished runs *rollable to a summary with per-log entry count*
(summary.batch_summary): how many ran, is every one healthy, are they all the same run,
what did each finally answer, how much work did the batch do, how big is each log in
estimated tokens, which individual logs are healthy, which individual logs actually
produced a non-None final assistant response, how many tool calls each individual log made,
how long (in characters) each log's final assistant response is, and how many entries each
individual log has. This module adds the per-log *message count* detail that summary
deliberately left out — how many messages are in each individual log's LAST entry — so a
batch of runs can be checked for health/identity/outcome/size/health-per-log/
presence-per-log/tool-calls-per-log/final-response-len-per-log/entries-per-log AND per-log
message count in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_detail(paths) -> dict
        A read-only multi-run detail that composes the existing summary view
        (summary.batch_summary) with per-log message-count detail. Returns
        {runs, all_healthy, total_entries, max_estimated_tokens, identical_all,
        final_responses, tool_calls_total, estimated_tokens_per_log, healthy_per_log,
        has_final_response_per_log, tool_calls_per_log, final_response_len_per_log,
        entries_per_log, message_count_per_log}. Reuses batch_summary and
        inspect.summarize_log; does not re-implement either. Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .inspect import summarize_log
from .summary import batch_summary


def batch_detail(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run detail with per-log message count.

    Composes the existing summary view with per-log message-count detail. Keys:
      runs                 : int — from summary.batch_summary.
      all_healthy          : bool — from summary.batch_summary.
      total_entries        : int — from summary.batch_summary.
      max_estimated_tokens : int — from summary.batch_summary.
      identical_all        : bool — from summary.batch_summary.
      final_responses      : list[str | None] — from summary.batch_summary.
      tool_calls_total     : int — from summary.batch_summary.
      estimated_tokens_per_log : list[int] — from summary.batch_summary.
      healthy_per_log      : list[bool] — from summary.batch_summary.
      has_final_response_per_log : list[bool] — from summary.batch_summary.
      tool_calls_per_log   : list[int] — from summary.batch_summary.
      final_response_len_per_log : list[int] — from summary.batch_summary.
      entries_per_log      : list[int] — from summary.batch_summary.
      message_count_per_log : list[int] — [summarize_log(p)["message_count"] for p in paths],
                             aligned with the input order (one per log; that log's message
                             count: the length of its LAST entry's messages, 0 if none).

    The thirteen keys are taken directly from summary.batch_summary(paths); they are not
    re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = batch_summary(paths)

    message_count_per_log: list[int] = [summarize_log(p)["message_count"] for p in paths]

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
        "entries_per_log": report["entries_per_log"],
        "message_count_per_log": message_count_per_log,
    }
