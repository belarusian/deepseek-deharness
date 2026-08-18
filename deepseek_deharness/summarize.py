"""Multi-run rollup — one read-only report over many append-only logs.

Cycle 12 made a single run *auditable at a glance* (audit.audit_log) and Cycle
13 made two runs *comparable in one call* (compare.compare_logs). This module
rolls that up to N runs: given an iterable of log paths, it composes the
existing per-log views into a single multi-run report so a batch of finished
runs can be checked at once — how many ran, is every one healthy, how big is
the biggest, and are they all the same run?

One plain function, stdlib only, no plugin layer, no DI:

    summarize_runs(paths) -> dict
        A read-only rollup over an iterable of append-only log paths. Returns
        {runs, logs, all_healthy, total_entries, max_estimated_tokens,
        identical_all}. Reuses audit.audit_log (per-log report) and
        compare.compare_logs (pairwise identity); does not re-implement them.
        Never mutates any log file.
"""
from __future__ import annotations

from pathlib import Path

from .audit import audit_log
from .compare import compare_logs


def summarize_runs(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:
    """Return a single read-only rollup over an iterable of append-only logs.

    Composes the existing per-log views into one multi-run report. Keys:
      runs                 : int — number of log paths given.
      logs                 : list[dict] — [audit.audit_log(p) for p in paths].
      all_healthy          : bool — True iff every report is healthy (vacuously
                             True for an empty path list).
      total_entries        : int — sum of each report's `entries`.
      max_estimated_tokens : int — max of each report's `estimated_tokens`
                             (0 if there are no logs).
      identical_all        : bool — True iff every pair of logs is byte-identical
                             (reuse compare.compare_logs pairwise); vacuously True
                             for 0 or 1 log.

    This function never writes to or mutates any log file.
    """
    paths = list(paths)
    reports = [audit_log(p) for p in paths]

    all_healthy = all(rep["healthy"] for rep in reports)
    total_entries = sum(rep["entries"] for rep in reports)
    max_estimated_tokens = max((rep["estimated_tokens"] for rep in reports), default=0)

    identical_all = True
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if not compare_logs(paths[i], paths[j])["identical"]:
                identical_all = False
                break
        if not identical_all:
            break

    return {
        "runs": len(paths),
        "logs": reports,
        "all_healthy": all_healthy,
        "total_entries": total_entries,
        "max_estimated_tokens": max_estimated_tokens,
        "identical_all": identical_all,
    }
