"""Tests for replay & recovery (replay.py).

The append-only log is the source of truth. These tests prove a run can be
replayed from its log alone and a session recovered without re-calling the LLM.
"""
from __future__ import annotations

import pytest

from deepseek_deharness.log import Log
from deepseek_deharness.replay import reconstruct_session, replay
from deepseek_deharness.run import run
from deepseek_deharness.session import Session
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
    """Run a scripted multi-turn harness to a temp log; return (log_path, result)."""
    log_path = tmp_path / "log.jsonl"
    result = run(
        "add 2 and 3",
        model="m",
        tools=builtin_tools(),
        log_path=log_path,
        transport=_scripted_transport(),
    )
    return log_path, result


def test_reconstruct_session_recovers_final_messages(tmp_path):
    log_path, result = _run_to_log(tmp_path)
    recovered = reconstruct_session(log_path)
    # The recovered session holds the exact final conversation.
    assert recovered.messages == result["messages"]
    # It is a real Session, not a dict.
    assert isinstance(recovered, Session)
    # The last message is the assistant's final answer.
    assert recovered.messages[-1] == {"role": "assistant", "content": "the answer is 5"}


def test_replay_without_transport_does_not_call_llm(tmp_path):
    log_path, result = _run_to_log(tmp_path)

    # The pure re-read path takes no transport at all: it cannot call an LLM.
    out = replay(log_path)
    # Same final response as the original run.
    assert out["final_response"] == result["final_response"] == "the answer is 5"
    # Message count matches the recovered conversation.
    assert out["message_count"] == len(result["messages"])
    # The sentinel never fired (no LLM call) and no new log entry was appended.
    assert out["log_length"] == result["log_length"]


def test_replay_missing_log_returns_empty(tmp_path):
    missing = tmp_path / "does_not_exist.jsonl"
    session = reconstruct_session(missing)
    assert isinstance(session, Session)
    assert session.messages == []

    out = replay(missing)
    assert out["final_response"] is None
    assert out["messages"] == []
    assert out["message_count"] == 0
    assert out["log_length"] == 0


def test_replay_empty_log_returns_empty(tmp_path):
    empty = tmp_path / "empty.jsonl"
    Log(empty)  # creates an empty journal file
    session = reconstruct_session(empty)
    assert session.messages == []

    out = replay(empty)
    assert out["final_response"] is None
    assert out["message_count"] == 0
    assert out["log_length"] == 0


def test_replay_with_transport_continues_from_recovered_state(tmp_path):
    # Build a log that ends mid-conversation (a tool result, no final answer yet).
    log_path = tmp_path / "partial.jsonl"
    run(
        "add 2 and 3",
        model="m",
        tools=builtin_tools(),
        log_path=log_path,
        max_turns=1,  # stop after the tool turn -> no final answer in the log
        transport=_scripted_transport(),
    )
    entries = Log(log_path).read()
    assert len(entries) == 1
    assert entries[0]["step"]["tool_calls"][0]["name"] == "add"

    # A fresh transport that immediately returns a final answer.
    def finalizer(payload):
        return {"choices": [{"message": {"content": "recovered: 5"}}], "usage": {}}

    out = replay(log_path, transport=finalizer, max_turns=2)
    assert out["final_response"] == "recovered: 5"
    # The continuation appended a new reconciled entry to the same log.
    assert out["log_length"] == len(Log(log_path).read()) == 2


def test_replay_empty_log_with_transport_calls_llm(tmp_path):
    empty = tmp_path / "empty.jsonl"
    Log(empty)

    def finalizer(payload):
        return {"choices": [{"message": {"content": "fresh answer"}}], "usage": {}}

    out = replay(empty, transport=finalizer, max_turns=1)
    assert out["final_response"] == "fresh answer"
    assert out["log_length"] == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
