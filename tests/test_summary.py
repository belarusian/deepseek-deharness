"""Tests for the multi-run summary (summary.py).

Prove batch_summary composes rollout.batch_rollout into one consistent view with per-log
entry-count detail, reports health/identity/outcome/size/health-per-log/presence-per-log/
tool-calls-per-log/final-response-len-per-log/entries-per-log correctly across a summary,
and never mutates any input log.
"""
from __future__ import annotations

from deepseek_deharness.audit import audit_log
from deepseek_deharness.inspect import summarize_log
from deepseek_deharness.run import run
from deepseek_deharness.summary import batch_summary
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


def test_summary_two_identical_healthy_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    result = batch_summary([a, b])

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
    assert one_tool_calls > 0
    assert result["tool_calls_total"] == 2 * one_tool_calls
    # estimated_tokens_per_log: length 2, both > 0 and equal to that log's audit estimate.
    one_est = audit_log(a)["estimated_tokens"]
    assert one_est > 0
    assert len(result["estimated_tokens_per_log"]) == 2
    assert result["estimated_tokens_per_log"][0] == one_est
    assert result["estimated_tokens_per_log"][1] == one_est
    # healthy_per_log: [True, True].
    assert result["healthy_per_log"] == [True, True]
    # has_final_response_per_log: [True, True] — both logs produced a final response.
    assert result["has_final_response_per_log"] == [True, True]
    # tool_calls_per_log: [n, n] where n is one log's tool-call count (> 0).
    assert result["tool_calls_per_log"] == [one_tool_calls, one_tool_calls]
    # final_response_len_per_log: [L, L] where L is the character length of one log's
    # final response (> 0).
    one_fr = summarize_log(a)["final_response"]
    assert one_fr is not None
    one_len = len(one_fr)
    assert one_len > 0
    assert result["final_response_len_per_log"] == [one_len, one_len]
    # entries_per_log: [e, e] where e is one log's entry count (> 0).
    assert one_entries > 0
    assert result["entries_per_log"] == [one_entries, one_entries]


def test_summary_pair_with_one_corrupted_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    # B: same first line, then a corrupt (non-JSON) trailing line. Corrupt side is the 2nd log.
    lines = a.read_text().splitlines()
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join([lines[0], "{not valid json"]) + "\n")

    result = batch_summary([a, b])

    assert result["all_healthy"] is False
    assert result["identical_all"] is False
    # final_responses still has length 2 (one entry may be None for the corrupt side).
    assert len(result["final_responses"]) == 2
    # estimated_tokens_per_log still has length 2.
    assert len(result["estimated_tokens_per_log"]) == 2
    # healthy_per_log: [True, False] — the corrupt side is the second log.
    assert result["healthy_per_log"] == [True, False]
    # has_final_response_per_log reflects which logs produced a non-None final response;
    # it must be aligned to input order and consistent with final_responses.
    expected = [fr is not None for fr in result["final_responses"]]
    assert result["has_final_response_per_log"] == expected
    # The healthy first log did produce a final response.
    assert result["has_final_response_per_log"][0] is True
    # tool_calls_per_log still has length 2; the corrupt side's count reflects only its
    # parseable entries (the first line, which carries the tool call).
    assert len(result["tool_calls_per_log"]) == 2
    assert result["tool_calls_per_log"][0] == len(summarize_log(a)["tool_calls"])
    # final_response_len_per_log still has length 2; the corrupt side's length is 0 iff its
    # final response is None.
    assert len(result["final_response_len_per_log"]) == 2
    for i, fr in enumerate(result["final_responses"]):
        if fr is None:
            assert result["final_response_len_per_log"][i] == 0
        else:
            assert result["final_response_len_per_log"][i] == len(fr)
    # entries_per_log still has length 2; the corrupt side's count reflects only its
    # parseable entries (the first line).
    assert len(result["entries_per_log"]) == 2
    assert result["entries_per_log"][0] == summarize_log(a)["entries"]


def test_summary_never_mutates_any_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    before_a = a.read_bytes()
    before_b = b.read_bytes()
    batch_summary([a, b])
    after_a = a.read_bytes()
    after_b = b.read_bytes()

    assert before_a == after_a
    assert before_b == after_b


def test_summary_empty_path_list(tmp_path):
    result = batch_summary([])

    assert result["runs"] == 0
    assert result["all_healthy"] is True
    assert result["total_entries"] == 0
    assert result["max_estimated_tokens"] == 0
    assert result["identical_all"] is True
    assert result["final_responses"] == []
    assert result["tool_calls_total"] == 0
    assert result["estimated_tokens_per_log"] == []
    assert result["healthy_per_log"] == []
    assert result["has_final_response_per_log"] == []
    assert result["tool_calls_per_log"] == []
    assert result["final_response_len_per_log"] == []
    assert result["entries_per_log"] == []


def test_summary_single_log_one_entry(tmp_path):
    # A single healthy log with one entry: entries_per_log is [1].
    a = tmp_path / "a.jsonl"
    a.write_text(
        '{"step": {"turn": 1}, "messages": [{"role": "user", "content": "hi"}]}\n'
    )

    result = batch_summary([a])

    assert result["runs"] == 1
    assert result["entries_per_log"] == [1]
