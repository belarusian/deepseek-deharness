"""Log inspection & diff — human-readable views of the append-only log.

Cycle 4 made the source of truth *auditable* (verify) and *repairable*
(repair). This module makes it *inspectable*: a read-only summary of what is in
a log, and a pairwise comparison that finds where two logs diverge.

Two plain functions, stdlib only, no plugin layer, no DI:

    summarize_log(log_path) -> dict
        A read-only summary of an append-only log for humans/debugging. Returns
        {entries, message_count, roles, tool_calls, final_response, healthy}.
        Never mutates the log file.

    diff_logs(a_path, b_path) -> dict
        Compare two logs and return {a_entries, b_entries, common_prefix,
        divergent_at} where common_prefix is the number of leading entries that
        are byte-identical (same JSON line) and divergent_at is the first index
        at which they differ (None if one is a prefix of the other / identical).
"""
from __future__ import annotations

import json
from pathlib import Path

from .repair import verify_log


def _read_lines(log_path: str | Path) -> list[str]:
    """Return the raw non-blank lines of the log file (empty if missing)."""
    path = Path(log_path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return [line for line in fh if line.strip()]


def _parse(line: str) -> dict | None:
    """Parse one log line into a dict, or None if it is not valid JSON."""
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def summarize_log(log_path: str | Path) -> dict:
    """Return a read-only summary of an append-only log.

    Keys:
      entries         : int — number of log lines (entries).
      message_count   : int — length of the LAST entry's `messages` (0 if none).
      roles           : dict[str, int] — role counts across the LAST entry's messages.
      tool_calls      : list[dict] — for every tool call seen in any entry's `step`,
                        a record {index, name} in log order.
      final_response  : str | None — last assistant content in the LAST entry's messages.
      healthy         : bool — verify_log(log_path) == [].

    This function never writes to or mutates the log file.
    """
    lines = _read_lines(log_path)
    entries = len(lines)

    # Last parseable entry drives message_count / roles / final_response.
    last: dict | None = None
    for line in reversed(lines):
        obj = _parse(line)
        if obj is not None and isinstance(obj.get("messages"), list):
            last = obj
            break

    messages: list[dict] = (last or {}).get("messages", [])
    roles: dict[str, int] = {}
    for msg in messages:
        role = msg.get("role") if isinstance(msg, dict) else None
        if role is not None:
            roles[role] = roles.get(role, 0) + 1

    final_response: str | None = None
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content")
            if isinstance(content, str):
                final_response = content
            break

    tool_calls: list[dict] = []
    for idx, line in enumerate(lines):
        obj = _parse(line)
        if obj is None:
            continue
        step = obj.get("step")
        if not isinstance(step, dict):
            continue
        calls = step.get("tool_calls")
        if not isinstance(calls, list):
            continue
        for tc in calls:
            name = None
            if isinstance(tc, dict):
                fn = tc.get("function")
                if isinstance(fn, dict) and "name" in fn:
                    name = fn["name"]
                elif "name" in tc:
                    name = tc["name"]
            tool_calls.append({"index": idx, "name": name})

    return {
        "entries": entries,
        "message_count": len(messages),
        "roles": roles,
        "tool_calls": tool_calls,
        "final_response": final_response,
        "healthy": verify_log(log_path) == [],
    }


def diff_logs(a_path: str | Path, b_path: str | Path) -> dict:
    """Compare two append-only logs and locate their fork point.

    Keys:
      a_entries     : int — number of lines in log A.
      b_entries     : int — number of lines in log B.
      common_prefix : int — number of leading entries that are byte-identical.
      divergent_at  : int | None — first index where the two logs differ; None if
                      one is a prefix of the other or they are identical.
    """
    a_lines = _read_lines(a_path)
    b_lines = _read_lines(b_path)

    common_prefix = 0
    n = min(len(a_lines), len(b_lines))
    for i in range(n):
        if a_lines[i].strip() == b_lines[i].strip():
            common_prefix += 1
        else:
            break

    divergent_at: int | None
    if common_prefix < n:
        divergent_at = common_prefix
    elif len(a_lines) != len(b_lines):
        # One is a strict prefix of the other; they "diverge" at the shorter length.
        divergent_at = n
    else:
        divergent_at = None

    return {
        "a_entries": len(a_lines),
        "b_entries": len(b_lines),
        "common_prefix": common_prefix,
        "divergent_at": divergent_at,
    }
