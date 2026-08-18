"""Tests for side-by-side log comparison (compare.py).

Prove compare_logs composes audit_log + diff_logs into one consistent view,
reports identical vs diverging correctly, and never mutates either log.
"""
from __future__ import annotations

import json

from deepseek_deharness.compare import compare_logs
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


def test_compare_identical_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    result = compare_logs(a, b)

    assert result["identical"] is True
    assert result["divergent_at"] is None
    # Both per-log audit reports are present and equal.
    assert result["a"] == result["b"]
    assert result["a"]["entries"] > 0
    assert result["a"]["healthy"] is True


def test_compare_diverging_logs(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    # Build B: same first line, then a different second line.
    lines = a.read_text().splitlines()
    b_lines = [lines[0], json.dumps({"step": {"content": "different"}, "messages": []})]
    b = tmp_path / "b.jsonl"
    b.write_text("\n".join(b_lines) + "\n")

    result = compare_logs(a, b)

    assert result["identical"] is False
    assert result["divergent_at"] == 1
    # Both per-log audit fields are still populated.
    assert result["a"]["entries"] > 0
    assert result["b"]["entries"] > 0
    assert isinstance(result["a"]["healthy"], bool)
    assert isinstance(result["b"]["healthy"], bool)


def test_compare_never_mutates_either_log(tmp_path):
    a = _run_to_log(tmp_path, "a.jsonl")
    b = tmp_path / "b.jsonl"
    b.write_text(a.read_text())

    before_a = a.read_bytes()
    before_b = b.read_bytes()
    compare_logs(a, b)
    after_a = a.read_bytes()
    after_b = b.read_bytes()

    assert before_a == after_a
    assert before_b == after_b


def test_compare_empty_vs_nonempty(tmp_path):
    nonempty = _run_to_log(tmp_path, "nonempty.jsonl")
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")

    result = compare_logs(empty, nonempty)

    assert result["identical"] is False
    assert result["divergent_at"] == 0
    # Empty side: all-zero report, healthy.
    assert result["a"]["entries"] == 0
    assert result["a"]["healthy"] is True
    assert result["a"]["violations"] == []
    assert result["a"]["final_response"] is None
    assert result["a"]["tool_calls"] == 0
    assert result["a"]["estimated_tokens"] == 0
    # Non-empty side: populated report.
    assert result["b"]["entries"] > 0
    assert result["b"]["healthy"] is True
    assert result["b"]["final_response"] is not None
