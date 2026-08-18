"""Multi-run ledger — the manifest view plus per-log tool-call count in one view.

Cycle 18 made N finished runs *rollable to a manifest with per-log outcome
presence* (manifest.batch_manifest): how many ran, is every one healthy, are
they all the same run, what did each finally answer, how much work did the batch
do, how big is each log in estimated tokens, which individual logs are healthy,
and which individual logs actually produced a non-None final assistant response.
This module adds the per-log *tool-call count* detail that manifest deliberately
left out — how many tool calls each individual log made — so a batch of runs can
be checked for health/identity/outcome/size/health/presence AND per-log
tool-call count in one call.

One plain function, stdlib only, no plugin layer, no DI:

    batch_ledger(paths) -> dict
        A read-only multi-run ledger that composes the existing manifest view
        (manifest.batch_manifest) with per-log tool-call count detail. Returns
        {runs, all_healthy, total_entries, max_estimated_tokens, identical_all,
        final_responses, tool_calls_total, estimated_tokens_per_log,
        healthy_per_log, has_final_response_per_log, tool_calls_per_log}. Reuses
        batch_manifest and inspect.summarize_log; does not re-implement either.
        Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .inspect import summarize_log
from .manifest import batch_manifest


def batch_ledger(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only multi-run ledger with per-log tool-call count.

    Composes the existing manifest view with per-log tool-call count detail.
    Keys:
      runs                 : int — from manifest.batch_manifest.
      all_healthy          : bool — from manifest.batch_manifest.
      total_entries        : int — from manifest.batch_manifest.
      max_estimated_tokens : int — from manifest.batch_manifest.
      identical_all        : bool — from manifest.batch_manifest.
      final_responses      : list[str | None] — from manifest.batch_manifest.
      tool_calls_total     : int — from manifest.batch_manifest.
      estimated_tokens_per_log : list[int] — from manifest.batch_manifest.
      healthy_per_log      : list[bool] — from manifest.batch_manifest.
      has_final_response_per_log : list[bool] — from manifest.batch_manifest.
      tool_calls_per_log   : list[int] — [len(inspect.summarize_log(p)["tool_calls"])
                             for p in paths], aligned with the input order (one per
                             log; that log's tool-call count).

    The ten keys are taken directly from manifest.batch_manifest(paths); they are
    not re-derived. This function never writes to or mutates any log file.
    """
    paths = list(paths)
    report = batch_manifest(paths)

    tool_calls_per_log: list[int] = [
        len(summarize_log(p)["tool_calls"]) for p in paths
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
        "tool_calls_per_log": tool_calls_per_log,
    }
