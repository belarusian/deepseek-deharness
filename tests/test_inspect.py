"""Tests for log inspection & diff (inspect.py).

Prove summarize_log gives a correct read-only summary of an append-only log,
that it reports healthy=False on a truncated log while still returning the
recoverable fields, that it never mutates the log, and that diff_logs finds the
fork point between two logs.
"""
from __future__ import annotations

import json

from deepseek_deharness.inspect import diff_logs, summarize_log
from deepseek_deharness.run import run
from deepseek_deharness.tools import builtin_tools


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


def test_summarize_healthy_scripted_run(tmp_path):
    log_path = _run_to_log(tmp_path)
    s = summarize_log(log_path)
    # Two turns: turn 1 (tool call), turn 2 (final answer).
    assert s["entries"] == 2
    assert s["healthy"] is True
    # Last entry's messages: user, assistant(tool_call), tool, assistant(final).
    assert s["message_count"] == 4
    assert s["roles"]["assistant"] == 2
    assert s["roles"]["user"] == 1
    assert s["roles"]["tool"] == 1
    # One tool call seen in entry index 0.
    assert s["tool_calls"] == [{"index": 0, "name": "add"}]
    assert s["final_response"] == "the answer is 5"


def test_summarize_truncated_log_reports_unhealthy(tmp_path):
    log_path = _run_to_log(tmp_path)
    # Truncate the final line to a partial JSON object.
    lines = log_path.read_text().splitlines()
    truncated = "\n".join(lines[:-1]) + '\n{"step": {"content": "the ans'
    log_path.write_text(truncated + "\n")

    s = summarize_log(log_path)
    assert s["healthy"] is False
    # Still returns recoverable fields from the last *parseable* entry.
    assert s["entries"] == 2
    assert s["message_count"] >= 1
    assert isinstance(s["roles"], dict)


def test_diff_identical_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())
    d = diff_logs(a, b)
    assert d["a_entries"] == 2
    assert d["b_entries"] == 2
    assert d["common_prefix"] == 2
    assert d["divergent_at"] is None


def test_diff_diverging_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    # Build B: same first line, then a different second line.
    lines = a.read_text().splitlines()
    b_lines = [lines[0], json.dumps({"step": {"content": "different"}, "messages": []})]
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join(b_lines) + "\n")

    d = diff_logs(a, b)
    assert d["a_entries"] == 2
    assert d["b_entries"] == 2
    assert d["common_prefix"] == 1
    assert d["divergent_at"] == 1


def test_diff_prefix_of_other(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    lines = a.read_text().splitlines()
    b = tmp_path / "b.jsonl"
    # B is a strict prefix of A (only the first line).
    b.write_text(lines[0] + "\n")
    d = diff_logs(a, b)
    assert d["a_entries"] == 2
    assert d["b_entries"] == 1
    assert d["common_prefix"] == 1
    assert d["divergent_at"] == 1


def test_summarize_never_mutates_log(tmp_path):
    log_path = _run_to_log(tmp_path)
    before = log_path.read_bytes()
    summarize_log(log_path)
    after = log_path.read_bytes()
    assert before == after


def test_summarize_missing_file_is_empty_and_healthy(tmp_path):
    missing = tmp_path / "nope.jsonl"
    s = summarize_log(missing)
    assert s["entries"] == 0
    assert s["message_count"] == 0
    assert s["roles"] == {}
    assert s["tool_calls"] == []
    assert s["final_response"] is None
    assert s["healthy"] is True


def test_diff_missing_files(tmp_path):
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    d = diff_logs(a, b)
    assert d == {
        "a_entries": 0,
        "b_entries": 0,
        "common_prefix": 0,
        "divergent_at": None,
    }
