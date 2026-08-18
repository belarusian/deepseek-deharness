"""Tests for the multi-run rollup (summarize.py).

Prove summarize_runs composes audit_log + compare_logs into one consistent
multi-run report, reports health/identity correctly across a batch, and never
mutates any input log.
"""
from __future__ import annotations

import json

from deepseek_deharness.run import run
from deepseek_deharness.summarize import summarize_runs
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


def test_summarize_two_identical_healthy_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    result = summarize_runs([a, b])

    assert result["runs"] == 2
    assert result["all_healthy"] is True
    assert result["identical_all"] is True
    # total_entries is exactly twice one log's entries.
    assert result["total_entries"] == 2 * result["logs"][0]["entries"]
    assert result["max_estimated_tokens"] > 0
    # Both per-log reports are present and equal.
    assert result["logs"][0] == result["logs"][1]


def test_summarize_pair_with_one_corrupted_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    # B: same first line, then a corrupt (non-JSON) trailing line.
    lines = a.read_text().splitlines()
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join([lines[0], "{not valid json"]) + "\n")

    result = summarize_runs([a, b])

    assert result["all_healthy"] is False
    assert result["identical_all"] is False
    # The per-log `logs` list still holds both full reports.
    assert len(result["logs"]) == 2
    assert isinstance(result["logs"][0]["healthy"], bool)
    assert isinstance(result["logs"][1]["healthy"], bool)
    assert result["logs"][1]["healthy"] is False
    # The healthy side is still reported as healthy.
    assert result["logs"][0]["healthy"] is True


def test_summarize_never_mutates_any_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    before_a = a.read_bytes()
    before_b = b.read_bytes()
    summarize_runs([a, b])
    after_a = a.read_bytes()
    after_b = b.read_bytes()

    assert before_a == after_a
    assert before_b == after_b


def test_summarize_empty_path_list(tmp_path):
    result = summarize_runs([])

    assert result["runs"] == 0
    assert result["logs"] == []
    assert result["all_healthy"] is True
    assert result["total_entries"] == 0
    assert result["max_estimated_tokens"] == 0
    assert result["identical_all"] is True


def test_summarize_single_log_is_identical(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")

    result = summarize_runs([a])

    # A single log has no pairs to compare: identical_all is vacuously True.
    assert result["runs"] == 1
    assert result["identical_all"] is True
    assert result["all_healthy"] is True
    assert result["total_entries"] == result["logs"][0]["entries"]


def test_summarize_three_logs_not_all_identical(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())
    # c: a single-entry log with different content (still healthy), so it
    # diverges from a/b at entry 0 while remaining well-formed.
    c = tmp_path / "c.jsonl"
    c.write_text(json.dumps({"step": {"content": "different"}, "messages": []}) + "\n")

    result = summarize_runs([a, b, c])

    assert result["runs"] == 3
    # a==b but c differs from both, so not all identical.
    assert result["identical_all"] is False
    assert result["all_healthy"] is True
