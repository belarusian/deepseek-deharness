"""Token-budget planning for an append-only log.

Cycle 6 made the source of truth *traceable* and Cycle 7 made it *compactable*.
This module makes it *budgetable*: given a token budget, decide whether a finished
run already fits, and if not, plan the smallest compaction (largest per-entry
message count) that would bring it under budget.

Two plain functions, stdlib only, no plugin layer, no DI. Both are read-only with
respect to the original log — they reuse `compact.estimate_tokens` for the token
heuristic and `compact.compact_log` (which writes to a NEW temp file) to measure
the post-compaction size, so the source of truth is never mutated.

    fits_budget(log_path, max_tokens) -> bool
        True iff estimate_tokens(log_path) <= max_tokens.

    plan_compaction(log_path, max_tokens) -> dict
        {max_messages: int, fits_after: bool, estimated_tokens_after: int} where
        max_messages is the largest m in [0..len(messages of first entry)] such
        that compacting to m messages per entry yields an estimate <= max_tokens.
"""
from __future__ import annotations

import json
from pathlib import Path

from .compact import compact_log, estimate_tokens


def _read_lines(log_path: str | Path) -> list[str]:
    """Return the raw non-blank lines of the log file (empty if missing)."""
    path = Path(log_path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return [line for line in fh if line.strip()]


def _first_entry_message_count(log_path: str | Path) -> int:
    """Return len(messages) of the first parseable entry that has a message list.

    0 when the log is empty, missing, or no entry carries a message list. This is
    the upper bound for the per-entry compaction search in `plan_compaction`.
    """
    for line in _read_lines(log_path):
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict) and isinstance(obj.get("messages"), list):
            return len(obj["messages"])
    return 0


def fits_budget(log_path: str | Path, max_tokens: int) -> bool:
    """Return True iff the log's token estimate is within ``max_tokens``.

    Reuses `compact.estimate_tokens` (the documented heuristic, not a tokenizer).
    Read-only: never mutates the log file. An empty/missing log estimates to 0 and
    therefore fits any non-negative budget.
    """
    return estimate_tokens(log_path) <= max_tokens


def plan_compaction(log_path: str | Path, max_tokens: int) -> dict:
    """Plan the largest per-entry message count that fits a token budget.

    Binary-searches ``m`` over [0..len(messages of first entry)] for the largest m
    such that compacting to m messages per entry yields an estimate <= max_tokens.
    The post-compaction size is measured by writing a temp copy via
    `compact.compact_log` and running `compact.estimate_tokens` on it — the
    original log is never mutated.

    Returns:
      max_messages           : int — largest fitting m (0 if even m=0 exceeds budget).
      fits_after             : bool — whether that compaction lands within budget.
      estimated_tokens_after : int — token estimate of the compacted copy at that m.

    For an empty/missing log, returns {max_messages: 0, fits_after: True,
    estimated_tokens_after: 0}.
    """
    upper = _first_entry_message_count(log_path)
    if upper == 0:
        return {"max_messages": 0, "fits_after": True, "estimated_tokens_after": 0}

    # Monotonic predicate: estimate after compacting to m messages is non-decreasing
    # in m, so the set of fitting m is a prefix [0..k]. Binary search for the largest.
    lo, hi = 0, upper
    best_fit = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        result = compact_log(log_path, max_messages=mid)
        est = estimate_tokens(result["path"])
        if est <= max_tokens:
            best_fit = mid
            lo = mid + 1
        else:
            hi = mid - 1

    if best_fit < 0:
        # Even m=0 exceeds budget.
        result = compact_log(log_path, max_messages=0)
        return {
            "max_messages": 0,
            "fits_after": False,
            "estimated_tokens_after": estimate_tokens(result["path"]),
        }

    result = compact_log(log_path, max_messages=best_fit)
    est = estimate_tokens(result["path"])
    return {
        "max_messages": best_fit,
        "fits_after": est <= max_tokens,
        "estimated_tokens_after": est,
    }
