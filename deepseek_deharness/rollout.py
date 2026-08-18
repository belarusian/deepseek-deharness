"""Multi-run rollout — the ledger view plus per-log final-response length in one view.

Cycle 19 made N finished runs *rollable to a ledger with per-log tool-call count*
(ledger.batch_ledger): how many ran, is every one healthy, are they all the same run,
what did each finally answer, how much work did the batch do, how big is each log in
estimated tokens, which individual logs are healthy, which individual logs actually
produced a non-None final assistant response, and how many tool calls each individual
log made. This module adds the per-log *final-response length* detail that ledger
deliberately left out — how long (in characters) each log's final assistant response is,
0 when it produced none — so a batch of runs can be checked for health/identity/outcome/
size/health/presence/tool-calls-per-log AND per-log final-response length in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_rollout(paths) -> dict
        A read-only multi-run rollout that composes the existing ledger view
        (ledger.batch_ledger) with per-log final-response length detail. Returns
        {runs, all_healthy, total_entries, max_estimated_tokens, identical_all,
        final_responses, tool_calls_total, estimated_tokens_per_log, healthy_per_log,
        has_final_response_per_log, tool_calls_per_log, final_response_len_per_log}.
        Reuses batch_ledger; does not re-implement it. Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .ledger import batch_ledger


def batch_rollout(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run rollout with per-log final-response length.

    Composes the existing ledger view with per-log final-response length detail.
    Keys:
      runs                 : int — from ledger.batch_ledger.
      all_healthy          : bool — from ledger.batch_ledger.
      total_entries        : int — from ledger.batch_ledger.
      max_estimated_tokens : int — from ledger.batch_ledger.
      identical_all        : bool — from ledger.batch_ledger.
      final_responses      : list[str | None] — from ledger.batch_ledger.
      tool_calls_total     : int — from ledger.batch_ledger.
      estimated_tokens_per_log : list[int] — from ledger.batch_ledger.
      healthy_per_log      : list[bool] — from ledger.batch_ledger.
      has_final_response_per_log : list[bool] — from ledger.batch_ledger.
      tool_calls_per_log   : list[int] — from ledger.batch_ledger.
      final_response_len_per_log : list[int] — [len(fr) if fr is not None else 0 for
                             fr in report["final_responses"]], aligned with the input
                             order (one per log; that log's final-response character
                             length, 0 when it produced no final response).

    The eleven keys are taken directly from ledger.batch_ledger(paths); they are not
    re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = batch_ledger(paths)

    final_response_len_per_log: list[int] = [
        len(fr) if fr is not None else 0 for fr in report["final_responses"]
    ]

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
        "final_response_len_per_log": final_response_len_per_log,
    }
