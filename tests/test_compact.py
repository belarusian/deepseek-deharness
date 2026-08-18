"""Tests for log compaction & token estimation (compact.py).

Prove compact_log keeps steps intact while truncating message history, that it
never mutates the original log, and that estimate_tokens is a stable positive
heuristic (0 for empty/missing logs).
"""
from __future__ import annotations

import json
from pathlib import Path

from deepseek_deharness.compact import compact_log, estimate_tokens
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


def test_compact_keeps_steps_and_truncates_messages(tmp_path):
    log_path = _run_to_log(tmp_path)
    original_lines = log_path.read_text().splitlines()

    result = compact_log(log_path, max_messages=1)
    assert result["entries"] == 2
    assert result["messages_before"] >= result["messages_after"]
    assert Path(result["path"]).exists()

    compacted_lines = Path(result["path"]).read_text().splitlines()
    assert len(compacted_lines) == len(original_lines)

    # Steps are preserved intact; messages truncated to last 1.
    for i, line in enumerate(compacted_lines):
        entry = json.loads(line)
        orig_entry = json.loads(original_lines[i])
        assert entry["step"] == orig_entry["step"]
        assert len(entry["messages"]) <= 1


def test_compact_never_mutates_original(tmp_path):
    log_path = _run_to_log(tmp_path)
    before = log_path.read_bytes()
    compact_log(log_path, max_messages=1)
    after = log_path.read_bytes()
    assert before == after


def test_compact_zero_messages_drops_all(tmp_path):
    log_path = _run_to_log(tmp_path)
    result = compact_log(log_path, max_messages=0)
    assert result["messages_after"] == 0
    compacted_lines = Path(result["path"]).read_text().splitlines()
    for line in compacted_lines:
        entry = json.loads(line)
        assert entry["messages"] == []


def test_estimate_tokens_positive_and_zero(tmp_path):
    log_path = _run_to_log(tmp_path)
    assert estimate_tokens(log_path) > 0
    missing = tmp_path / "nope.jsonl"
    assert estimate_tokens(missing) == 0
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    assert estimate_tokens(empty) == 0


def test_compact_negative_max_raises(tmp_path):
    log_path = _run_to_log(tmp_path)
    try:
        compact_log(log_path, max_messages=-1)
        raised = False
    except ValueError:
        raised = True
    assert raised

