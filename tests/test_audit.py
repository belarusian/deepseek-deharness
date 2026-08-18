"""Tests for the log health audit (audit.py).

Prove audit_log composes verify/summarize/estimate into one consistent view,
reports healthy vs corrupted correctly, and never mutates the original log.
"""
from __future__ import annotations

from deepseek_deharness.audit import audit_log
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


def test_audit_healthy_two_turn_log(tmp_path):
    log_path = _run_to_log(tmp_path)
    report = audit_log(log_path)

    assert report["entries"] > 0
    assert report["healthy"] is True
    assert report["violations"] == []
    assert report["final_response"] is not None
    assert report["tool_calls"] >= 1
    assert report["estimated_tokens"] > 0


def test_audit_corrupted_log_reports_violation_but_recovers_fields(tmp_path):
    log_path = _run_to_log(tmp_path)
    # Append a truncated/invalid JSON tail line to a copy.
    corrupt = tmp_path / "corrupt.jsonl"
    corrupt.write_text(log_path.read_text() + '{"step": {"content": "trunc')

    report = audit_log(corrupt)

    assert report["healthy"] is False
    assert len(report["violations"]) >= 1
    # Recoverable fields are still present and sensible.
    assert report["entries"] > 0
    assert report["final_response"] is not None
    assert report["tool_calls"] >= 1
    assert report["estimated_tokens"] > 0


def test_audit_never_mutates_original(tmp_path):
    log_path = _run_to_log(tmp_path)
    before = log_path.read_bytes()
    audit_log(log_path)
    after = log_path.read_bytes()
    assert before == after


def test_audit_empty_and_missing_log(tmp_path):
    missing = tmp_path / "nope.jsonl"
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")

    for path in (missing, empty):
        report = audit_log(path)
        assert report["entries"] == 0
        assert report["healthy"] is True
        assert report["violations"] == []
        assert report["final_response"] is None
        assert report["tool_calls"] == 0
        assert report["estimated_tokens"] == 0
