"""Tests for log repair & verification (repair.py).

The append-only log is the source of truth; these tests prove its invariants
can be verified and a truncated/corrupt trailing entry can be repaired without
touching any healthy entry.
"""
from __future__ import annotations

import json

import pytest

from deepseek_deharness.log import Log
from deepseek_deharness.repair import repair_log, verify_log
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


def _run_to_log(tmp_path):
    """Run a scripted two-turn harness to a temp log; return the log path."""
    log_path = tmp_path / "log.jsonl"
    run(
        "add 2 and 3",
        model="m",
        tools=builtin_tools(),
        log_path=log_path,
        transport=_scripted_transport(),
    )
    return log_path


def test_healthy_log_verifies_clean(tmp_path):
    # A real scripted run produces a healthy append-only log.
    log_path = _run_to_log(tmp_path)
    assert len(Log(log_path).read()) == 2
    # verify_log reports no violations for a healthy log.
    assert verify_log(log_path) == []


def test_truncated_final_line_detected_and_repaired(tmp_path):
    log_path = _run_to_log(tmp_path)
    # Corrupt the log by appending a truncated (partial JSON) final line, as an
    # interrupted write would leave behind.
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write('{"step": {"content": "the answer is 5"}, "messages": [')

    # verify_log detects the trailing bad_json violation (and nothing else).
    violations = verify_log(log_path)
    assert any(v["type"] == "bad_json" for v in violations)

    # repair_log drops exactly the one corrupt trailing entry and keeps the rest.
    result = repair_log(log_path)
    assert result == {"repaired": True, "dropped": 1, "entries_after": 2}

    # The repaired log verifies clean again and still holds the two healthy turns.
    assert verify_log(log_path) == []
    entries = Log(log_path).read()
    assert len(entries) == 2
    assert entries[-1]["step"]["content"] == "the answer is 5"


def test_mid_conversation_mutation_flagged(tmp_path):
    log_path = _run_to_log(tmp_path)
    entries = Log(log_path).read()
    # Mutate entry 1 so its messages no longer extend entry 0 by prefix: drop the
    # first message (a mid-conversation mutation, not a shrink of the whole list).
    mutated = json.loads(json.dumps(entries[1]))
    mutated["messages"] = entries[1]["messages"][1:]
    assert len(mutated["messages"]) >= len(entries[0]["messages"])  # not a shrink

    with log_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(entries[0], sort_keys=True) + "\n")
        fh.write(json.dumps(mutated, sort_keys=True) + "\n")

    violations = verify_log(log_path)
    assert any(v["type"] == "prefix_violation" for v in violations)


def test_repair_healthy_log_is_noop(tmp_path):
    log_path = _run_to_log(tmp_path)
    result = repair_log(log_path)
    assert result == {"repaired": False, "dropped": 0, "entries_after": 2}
    # The healthy entries are untouched.
    assert verify_log(log_path) == []


def test_messages_shrink_flagged(tmp_path):
    log_path = _run_to_log(tmp_path)
    entries = Log(log_path).read()
    # Mutate entry 1 so its messages list is strictly shorter than entry 0's.
    mutated = json.loads(json.dumps(entries[1]))
    mutated["messages"] = entries[1]["messages"][: len(entries[0]["messages"]) - 1]

    with log_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(entries[0], sort_keys=True) + "\n")
        fh.write(json.dumps(mutated, sort_keys=True) + "\n")

    violations = verify_log(log_path)
    assert any(v["type"] == "messages_shrank" for v in violations)


def test_repair_drops_multiple_trailing_corrupt_entries(tmp_path):
    log_path = _run_to_log(tmp_path)
    with log_path.open("a", encoding="utf-8") as fh:
        # Two trailing corrupt entries: a partial JSON line and a non-dict line.
        fh.write('{"step": {"content": "x"}, "messages": [\n')
        fh.write("[1, 2, 3]\n")

    result = repair_log(log_path)
    assert result == {"repaired": True, "dropped": 2, "entries_after": 2}
    assert verify_log(log_path) == []


def test_verify_missing_and_empty_log(tmp_path):
    # A missing log and an empty log both verify clean (nothing to violate).
    assert verify_log(tmp_path / "nope.jsonl") == []
    Log(tmp_path / "empty.jsonl")  # creates an empty journal file
    assert verify_log(tmp_path / "empty.jsonl") == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
