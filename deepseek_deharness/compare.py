"""Side-by-side log comparison — one read-only view over two append-only logs.

Cycle 12 made a single run *auditable at a glance* (audit.audit_log) and Cycle 5
made two runs *diffable* (inspect.diff_logs). This module composes those two
plain functions into a single side-by-side health comparison so two finished
runs can be checked against each other in one call: are they the same run, where
do they fork, and is each one healthy?

One plain function, stdlib only, no plugin layer, no DI:

    compare_logs(a_path, b_path) -> dict
        A read-only side-by-side health comparison of two append-only logs.
        Returns {a, b, identical, divergent_at} where a/b are the full
        audit.audit_log reports for each log, identical is True iff the two logs
        are byte-identical line-for-line, and divergent_at is the first index at
        which they differ (None if identical). Reuses audit.audit_log and
        inspect.diff_logs (does not re-implement them). Never mutates either log.
"""
from __future__ import annotations

from pathlib import Path

from .audit import audit_log
from .inspect import diff_logs


def compare_logs(a_path: str | Path, b_path: str | Path) -> dict:
    """Return a read-only side-by-side health comparison of two append-only logs.

    Composes the existing per-concern functions into one view. Keys:
      a            : dict — full audit.audit_log report for log A.
      b            : dict — full audit.audit_log report for log B.
      identical    : bool — True iff the two logs are byte-identical line-for-line
                        (diff divergent_at is None AND a_entries == b_entries).
      divergent_at : int | None — first index where the two logs differ; None if
                        identical (from inspect.diff_logs).

    This function never writes to or mutates either log file.
    """
    diff = diff_logs(a_path, b_path)
    identical = diff["divergent_at"] is None and diff["a_entries"] == diff["b_entries"]

    return {
        "a": audit_log(a_path),
        "b": audit_log(b_path),
        "identical": identical,
        "divergent_at": diff["divergent_at"],
    }
