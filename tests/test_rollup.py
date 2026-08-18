"""Tests for the multi-run rollup (rollup.py).

Prove rollup_runs composes aggregate_runs + audit_log into one consistent view
with per-log size detail, reports health/identity/outcome/size correctly across
a batch, and never mutates any input log.
"""
from __future__ import annotations

import json

from deepseek_deharness.audit import audit_log
from deepseek_deharness.inspect import summarize_log
from deepseek_deharness.rollup import rollup_runs
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


def test_rollup_two_identical_healthy_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    result = rollup_runs([a, b])

    assert result["runs"] == 2
    assert result["all_healthy"] is True
    assert result["identical_all"] is True
    # total_entries is exactly twice one log's entries.
    one_entries = summarize_log(a)["entries"]
    assert result["total_entries"] == 2 * one_entries
    assert result["max_estimated_tokens"] > 0
    # final_responses: length 2, both equal and non-None.
    assert len(result["final_responses"]) == 2
    assert result["final_responses"][0] is not None
    assert result["final_responses"][0] == result["final_responses"][1]
    # tool_calls_total is exactly twice one log's tool-call count.
    one_tool_calls = len(summarize_log(a)["tool_calls"])
    assert result["tool_calls_total"] == 2 * one_tool_calls
    # estimated_tokens_per_log: length 2, both equal to that log's audit estimate (> 0).
    one_est = audit_log(a)["estimated_tokens"]
    assert one_est > 0
    assert len(result["estimated_tokens_per_log"]) == 2
    assert result["estimated_tokens_per_log"][0] == one_est
    assert result["estimated_tokens_per_log"][1] == one_est


def test_rollup_pair_with_one_corrupted_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    # B: same first line, then a corrupt (non-JSON) trailing line.
    lines = a.read_text().splitlines()
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join([lines[0], "{not valid json"]) + "\n")

    result = rollup_runs([a, b])

    assert result["all_healthy"] is False
    assert result["identical_all"] is False
    # final_responses still has length 2 (one entry may be None for the corrupt side).
    assert len(result["final_responses"]) == 2
    # estimated_tokens_per_log still has length 2.
    assert len(result["estimated_tokens_per_log"]) == 2


def test_rollup_never_mutates_any_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    before_a = a.read_bytes()
    before_b = b.read_bytes()
    rollup_runs([a, b])
    after_a = a.read_bytes()
    after_b = b.read_bytes()

    assert before_a == after_a
    assert before_b == after_b


def test_rollup_empty_path_list(tmp_path):
    result = rollup_runs([])

    assert result["runs"] == 0
    assert result["all_healthy"] is True
    assert result["total_entries"] == 0
    assert result["max_estimated_tokens"] == 0
    assert result["identical_all"] is True
    assert result["final_responses"] == []
    assert result["tool_calls_total"] == 0
    assert result["estimated_tokens_per_log"] == []


def test_rollup_single_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")

    result = rollup_runs([a])

    # A single log has no pairs to compare: identical_all is vacuously True.
    assert result["runs"] == 1
    assert result["identical_all"] is True
    assert result["all_healthy"] is True
    assert len(result["final_responses"]) == 1
    assert result["tool_calls_total"] == len(summarize_log(a)["tool_calls"])
    # estimated_tokens_per_log has one entry equal to the log's audit estimate.
    assert result["estimated_tokens_per_log"] == [audit_log(a)["estimated_tokens"]]


def test_rollup_final_response_none_when_no_assistant_content(tmp_path):
    # A single-entry log with no assistant message: final_response is None.
    c = tmp_path / "c.jsonl"
    c.write_text(json.dumps({"step": {"content": "no assistant"}, "messages": []}) + "\n")

    result = rollup_runs([c])

    assert result["runs"] == 1
    assert result["final_responses"] == [None]
    # estimated_tokens_per_log still has one entry (the log's audit estimate).
    assert len(result["estimated_tokens_per_log"]) == 1
