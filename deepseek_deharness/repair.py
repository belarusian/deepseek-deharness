"""Log repair & verification — the append-only log's invariants, made checkable.

Cycle 1 declared the append-only log the single source of truth for
reconciliation; Cycle 3 made a run recoverable from its log alone. This module
makes that trust *auditable*: it can verify the log's invariants and repair a
log whose trailing entry(ies) were truncated or corrupted (e.g. a partial JSON
line written by an interrupted process).

Two plain functions, stdlib only, no plugin layer, no DI:

    verify_log(log_path) -> list[dict]
        Check the append-only log's invariants and return one violation record
        per problem found (an empty list means the log is healthy). Invariants:
          1. every entry has a `step` dict and a `messages` list;
          2. `messages` length is monotonically non-decreasing across entries;
          3. each entry's `messages` extends the previous entry's by prefix
             (no mid-conversation mutation).
        A line that is not valid JSON is reported as a violation too, so a
        truncated final line is detected here and repaired there.

    repair_log(log_path) -> dict
        Drop only the trailing corrupt entry(ies) — entries that fail to parse
        as JSON or lack the `step`/`messages` keys — and return
        {repaired: bool, dropped: int, entries_after: int}. Healthy entries are
        never touched; a log with no trailing corruption is a no-op.
"""
from __future__ import annotations

import json
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


def _is_well_formed(entry: dict) -> bool:
    """True if an entry has a `step` dict and a `messages` list."""
    return isinstance(entry.get("step"), dict) and isinstance(
        entry.get("messages"), list
    )


def verify_log(log_path: str | Path) -> list[dict]:
    """Verify the append-only log's invariants.

    Returns a list of violation records; an empty list means the log is healthy.
    Each record has ``index`` (0-based), ``type`` and ``detail`` keys. The three
    invariants checked are: (1) every entry has a `step` dict and a `messages`
    list; (2) `messages` length never decreases across entries; (3) each entry's
    `messages` extends the previous entry's by prefix. A line that is not valid
    JSON is reported as a ``bad_json`` violation.
    """
    violations: list[dict] = []
    lines = _read_lines(log_path)

    entries: list[dict | None] = []
    for i, line in enumerate(lines):
        obj = _parse(line)
        if obj is None:
            violations.append(
                {
                    "index": i,
                    "type": "bad_json",
                    "detail": f"line {i} is not valid JSON (truncated or corrupt)",
                }
            )
        entries.append(obj)

    prev_messages: list | None = None
    for i, entry in enumerate(entries):
        if entry is None:
            continue  # already reported as bad_json above
        if not _is_well_formed(entry):
            violations.append(
                {
                    "index": i,
                    "type": "malformed_entry",
                    "detail": (
                        f"entry {i} lacks a `step` dict and/or a `messages` list"
                    ),
                }
            )
            continue

        messages = entry["messages"]
        if prev_messages is not None:
            if len(messages) < len(prev_messages):
                violations.append(
                    {
                        "index": i,
                        "type": "messages_shrank",
                        "detail": (
                            f"entry {i} has {len(messages)} messages but entry "
                            f"{i - 1} had {len(prev_messages)} (append-only log "
                            "must never shrink)"
                        ),
                    }
                )
            elif not _is_prefix(prev_messages, messages):
                violations.append(
                    {
                        "index": i,
                        "type": "prefix_violation",
                        "detail": (
                            f"entry {i} does not extend entry {i - 1}'s messages "
                            "by prefix (mid-conversation mutation)"
                        ),
                    }
                )
        prev_messages = messages

    return violations


def repair_log(log_path: str | Path) -> dict:
    """Repair a log by dropping only its trailing corrupt entry(ies).

    An entry is considered corrupt if it fails to parse as JSON or lacks the
    `step`/`messages` keys. Only the *trailing* run of such entries is dropped;
    any healthy prefix is preserved byte-for-byte. Returns a dict with:
      repaired     : bool  (True iff at least one entry was dropped)
      dropped      : int   (number of trailing corrupt entries removed)
      entries_after: int   (number of healthy entries remaining)

    A log with no trailing corruption is a no-op ({repaired: False, dropped: 0}).
    """
    path = Path(log_path)
    lines = _read_lines(path)

    # Find the first index from which every entry is corrupt; drop that suffix.
    cut = len(lines)
    while cut > 0 and not _is_well_formed(_parse(lines[cut - 1]) or {}):
        cut -= 1

    dropped = len(lines) - cut
    if dropped == 0:
        return {"repaired": False, "dropped": 0, "entries_after": len(lines)}

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for line in lines[:cut]:
            fh.write(line if line.endswith("\n") else line + "\n")

    return {"repaired": True, "dropped": dropped, "entries_after": cut}


def _is_prefix(prefix: list, whole: list) -> bool:
    """True if `whole` starts with exactly `prefix` (same length or longer)."""
    if len(whole) < len(prefix):
        return False
    return all(a == b for a, b in zip(prefix, whole))
