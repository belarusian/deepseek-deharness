"""Multi-run manifest — the batch view plus per-log final-response presence in one view.

Cycle 17 made N finished runs *rollable to a batch with per-log health* (batch.
batch_report): how many ran, is every one healthy, are they all the same run,
what did each finally answer, how much work did the batch do, how big is each
log in estimated tokens, and which individual logs are healthy. This module adds
the per-log *final-response presence* detail that batch deliberately left out —
whether each log actually produced a non-None final assistant response — so a
batch of runs can be checked for health/identity/outcome/size/health AND
per-log outcome presence in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_manifest(paths) -> dict
        A read-only multi-run manifest that composes the existing batch view
        (batch.batch_report) with per-log final-response presence detail.
        Returns {runs, all_healthy, total_entries, max_estimated_tokens,
        identical_all, final_responses, tool_calls_total, estimated_tokens_per_log,
        healthy_per_log, has_final_response_per_log}. Reuses batch_report; does
        not re-implement it. Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .batch import batch_report


def batch_manifest(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run manifest with per-log presence detail.

    Composes the existing batch view with per-log final-response presence detail.
    Keys:
      runs                 : int — from batch.batch_report.
      all_healthy          : bool — from batch.batch_report.
      total_entries        : int — from batch.batch_report.
      max_estimated_tokens : int — from batch.batch_report.
      identical_all        : bool — from batch.batch_report.
      final_responses      : list[str | None] — from batch.batch_report.
      tool_calls_total     : int — from batch.batch_report.
      estimated_tokens_per_log : list[int] — from batch.batch_report.
      healthy_per_log      : list[bool] — from batch.batch_report.
      has_final_response_per_log : list[bool] — [fr is not None for fr in
                             batch_report(paths)["final_responses"]], aligned with
                             the input order (one per log; True iff that log
                             produced a non-None final assistant response).

    The nine keys are taken directly from batch.batch_report(paths); they are not
    re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = batch_report(paths)

    has_final_response_per_log: list[bool] = [
        fr is not None for fr in report["final_responses"]
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
        "has_final_response_per_log": has_final_response_per_log,
    }
