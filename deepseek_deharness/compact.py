"""Log compaction & token estimation — context-window management for the log.

Cycle 6 made the source of truth *traceable* (per-turn views). This module makes
it *compactable*: produce a truncated copy of an append-only log that fits a
context window (keeping every entry's `step` intact but trimming each entry's
message history), plus a cheap token estimate for budgeting.

Two plain functions, stdlib only, no plugin layer, no DI:

    compact_log(log_path, max_messages) -> dict
        Write a compacted copy to a NEW temp file; return {path, entries,
        messages_before, messages_after}. Never mutates the original log.

    estimate_tokens(log_path) -> int
        A cheap token estimate (sum of len(json.dumps(entry)) // 4 per entry).
        A documented heuristic, not a real tokenizer.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path


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


def compact_log(log_path: str | Path, max_messages: int) -> dict:
    """Write a compacted copy of an append-only log to a NEW temp file.

    Every entry's `step` is preserved intact; each entry's `messages` list is
    truncated to its last `max_messages` items (order preserved). Entries that
    are not valid JSON are copied through verbatim so the compacted log keeps
    the same line count as the original. The original log file is never
    mutated.

    Returns:
      path            : str — path of the newly written compacted file.
      entries         : int — number of lines in the (original) log.
      messages_before : int — total message items across all parseable entries.
      messages_after  : int — total message items after truncation.
    """
    if max_messages < 0:
        raise ValueError("max_messages must be >= 0")

    lines = _read_lines(log_path)
    out_lines: list[str] = []
    messages_before = 0
    messages_after = 0

    for line in lines:
        obj = _parse(line)
        if obj is None or not isinstance(obj.get("messages"), list):
            # Copy through verbatim (non-JSON entry, or entry without a message list).
            out_lines.append(line.strip())
            continue
        msgs = obj["messages"]
        messages_before += len(msgs)
        truncated = msgs[-max_messages:] if max_messages > 0 else []
        messages_after += len(truncated)
        compacted = dict(obj)
        compacted["messages"] = truncated
        out_lines.append(json.dumps(compacted, sort_keys=True))

    fd, tmp_path = tempfile.mkstemp(prefix="deh-compact-", suffix=".jsonl")
    with open(fd, "w", encoding="utf-8") as fh:
        for line in out_lines:
            fh.write(line + "\n")

    return {
        "path": tmp_path,
        "entries": len(lines),
        "messages_before": messages_before,
        "messages_after": messages_after,
    }


def estimate_tokens(log_path: str | Path) -> int:
    """Return a cheap token estimate for an append-only log.

    Heuristic: sum of ``len(json.dumps(entry)) // 4`` over every line (parsed or
    raw). This is intentionally not a real tokenizer — it is a stable, dependency-
    free proxy for relative size so callers can budget context windows. Returns 0
    for an empty or missing log.
    """
    total = 0
    for line in _read_lines(log_path):
        obj = _parse(line)
        # Use the parsed object when available (canonical form), else the raw line.
        text = json.dumps(obj, sort_keys=True) if obj is not None else line.strip()
        total += len(text) // 4
    return total
