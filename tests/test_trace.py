"""Tests for trajectory extraction & stats (trace.py).

Prove extract_trajectory reconstructs a correct per-turn trajectory from an
append-only log, that trajectory_stats aggregates correctly, that neither
function mutates the log, and that a truncated log still yields its leading turns.
"""
from __future__ import annotations

import json

from deepseek_deharness.run import run
from deepseek_deharness.tools import builtin_tools
from deepseek_deharness.trace import extract_trajectory, trajectory_stats


def _scripted_transport():
    calls = {"n": 0}

    def t(payload):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "c1",
                                    "type": "function",
                                    "function": {
                                        "name": "add",
                                        "arguments": '{"a": 2, "b": 3}',
                                    },
                                }
                            ],
                        }
                    }
                ],
                "usage": {},
            }
        return {"choices": [{"message": {"content": "the answer is 5"}}], "usage": {}}

    return t


def _run_to_log(tmp_path, name="log.jsonl"):
    log_path = tmp_path / name
    run(
        "add 2 and 3",
        model="m",
        tools=builtin_tools(),
        log_path=log_path,
        transport=_scripted_transport(),
    )
    return log_path


def test_extract_trajectory_two_turns(tmp_path):
    log_path = _run_to_log(tmp_path)
    traj = extract_trajectory(log_path)
    assert len(traj) == 2
    # Turn 0: tool call, no content.
    assert traj[0]["turn"] == 0
    assert traj[0]["content"] is None
    assert traj[0]["tool_calls"] == ["add"]
    assert isinstance(traj[0]["tool_results"], list) and len(traj[0]["tool_results"]) == 1
    # Turn 1: final answer, no tool calls.
    assert traj[1]["turn"] == 1
    assert traj[1]["content"] == "the answer is 5"
    assert traj[1]["tool_calls"] == []
    assert traj[1]["tool_results"] == []


def test_trajectory_stats(tmp_path):
    log_path = _run_to_log(tmp_path)
    stats = trajectory_stats(log_path)
    assert stats["turns"] == 2
    assert stats["total_tool_calls"] == 1
    assert stats["tools_used"] == {"add": 1}
    assert stats["final_response"] == "the answer is 5"


def test_never_mutates_log(tmp_path):
    log_path = _run_to_log(tmp_path)
    before = log_path.read_bytes()
    extract_trajectory(log_path)
    trajectory_stats(log_path)
    after = log_path.read_bytes()
    assert before == after


def test_truncated_log_returns_leading_turns(tmp_path):
    log_path = _run_to_log(tmp_path)
    lines = log_path.read_text().splitlines()
    truncated = "\n".join(lines[:-1]) + '\n{"step": {"content": "the ans'
    log_path.write_text(truncated + "\n")

    traj = extract_trajectory(log_path)
    # Only the first (parseable) entry survives; the truncated tail is skipped.
    assert len(traj) == 1
    assert traj[0]["turn"] == 0
    assert traj[0]["tool_calls"] == ["add"]

    stats = trajectory_stats(log_path)
    assert stats["turns"] == 1
    assert stats["total_tool_calls"] == 1
    assert stats["final_response"] is None


def test_missing_file_is_empty(tmp_path):
    missing = tmp_path / "nope.jsonl"
    assert extract_trajectory(missing) == []
    assert trajectory_stats(missing) == {
        "turns": 0,
        "total_tool_calls": 0,
        "tools_used": {},
        "final_response": None,
    }


def test_multiple_tool_calls_counted(tmp_path):
    # Hand-build a log with one entry requesting two tools.
    log_path = tmp_path / "multi.jsonl"
    entry = {
        "step": {
            "content": None,
            "tool_calls": [
                {"id": "a", "type": "function",
                 "function": {"name": "add", "arguments": "{}"}},
                {"id": "b", "type": "function",
                 "function": {"name": "mul", "arguments": "{}"}},
            ],
            "tool_results": [
                {"name": "add", "result": 5},
                {"name": "mul", "result": 6},
            ],
        },
        "messages": [],
    }
    log_path.write_text(json.dumps(entry, sort_keys=True) + "\n")

    traj = extract_trajectory(log_path)
    assert traj[0]["tool_calls"] == ["add", "mul"]
    assert len(traj[0]["tool_results"]) == 2

    stats = trajectory_stats(log_path)
    assert stats["total_tool_calls"] == 2
    assert stats["tools_used"] == {"add": 1, "mul": 1}
