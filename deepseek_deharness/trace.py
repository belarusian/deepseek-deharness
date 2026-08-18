"""Trajectory extraction & stats — per-turn views of the append-only log.

Cycle 5 made the source of truth *inspectable* (summarize/diff). This module
makes it *traceable*: reconstruct a clean per-turn trajectory from a log and
compute aggregate statistics over it, so a finished run can be walked turn by
turn without re-running the LLM.

Two plain functions, stdlib only, no plugin layer, no DI:

    extract_trajectory(log_path) -> list[dict]
        One record per log entry: {turn, content, tool_calls, tool_results}.

    trajectory_stats(log_path) -> dict
        Aggregate stats over the whole log: {turns, total_tool_calls,
        tools_used, final_response}.

Neither function mutates the log file.
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


def _tool_names(step: dict) -> list[str | None]:
    """Return the tool names requested in a step's `tool_calls` (in order)."""
    calls = step.get("tool_calls")
    if not isinstance(calls, list):
        return []
    names: list[str | None] = []
    for tc in calls:
        name = None
        if isinstance(tc, dict):
            fn = tc.get("function")
            if isinstance(fn, dict) and "name" in fn:
                name = fn["name"]
            elif "name" in tc:
                name = tc["name"]
        names.append(name)
    return names


def extract_trajectory(log_path: str | Path) -> list[dict]:
    """Reconstruct a clean per-turn trajectory from an append-only log.

    Returns one record per *parseable* entry, in log order:
      turn         : int — 0-based index of the entry.
      content      : str | None — the step's `content`.
      tool_calls   : list[str] — tool names requested in this entry's step.
      tool_results : list[dict] — mirrors the step's `tool_results` (empty if none).

    Entries that are not valid JSON (e.g. a truncated tail) are skipped, so a
    partially-written log still yields its recoverable leading turns. Never
    mutates the log file.
    """
    trajectory: list[dict] = []
    for idx, line in enumerate(_read_lines(log_path)):
        obj = _parse(line)
        if obj is None:
            continue
        step = obj.get("step")
        if not isinstance(step, dict):
            continue
        results = step.get("tool_results")
        trajectory.append(
            {
                "turn": idx,
                "content": step.get("content"),
                "tool_calls": _tool_names(step),
                "tool_results": results if isinstance(results, list) else [],
            }
        )
    return trajectory


def trajectory_stats(log_path: str | Path) -> dict:
    """Compute aggregate statistics over an append-only log.

    Returns:
      turns             : int — number of parseable entries (turns).
      total_tool_calls  : int — total tool calls across all turns.
      tools_used        : dict[str, int] — count of each tool name used.
      final_response    : str | None — the last non-None step content seen.

    Never mutates the log file.
    """
    trajectory = extract_trajectory(log_path)
    tools_used: dict[str, int] = {}
    total_tool_calls = 0
    final_response: str | None = None
    for record in trajectory:
        for name in record["tool_calls"]:
            total_tool_calls += 1
            if name is not None:
                tools_used[name] = tools_used.get(name, 0) + 1
        if record["content"] is not None:
            final_response = record["content"]

    return {
        "turns": len(trajectory),
        "total_tool_calls": total_tool_calls,
        "tools_used": tools_used,
        "final_response": final_response,
    }
