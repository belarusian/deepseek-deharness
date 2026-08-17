"""End-to-end tests for the four algebra (run.py).

inner spoke = work + trajectory; outer spoke = append-only log reconciliation.
We drive it with a scripted transport: turn 1 asks for a tool call, turn 2
returns the final answer.
"""
from __future__ import annotations

from deepseek_deharness.log import Log
from deepseek_deharness.run import inner_spoke, outer_spoke, run
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


def test_run_executes_tool_then_final(tmp_path):
    result = run(
        "add 2 and 3",
        model="m",
        tools=builtin_tools(),
        log_path=tmp_path / "log.jsonl",
        transport=_scripted_transport(),
    )
    assert result["final_response"] == "the answer is 5"
    # The append-only log was reconciled: one entry per turn (2 turns).
    assert result["log_length"] == 2
    log = Log(tmp_path / "log.jsonl")
    entries = log.read()
    assert len(entries) == 2
    # Turn 1 recorded the tool call; turn 2 the final content.
    assert entries[0]["step"]["tool_calls"][0]["name"] == "add"
    assert entries[1]["step"]["content"] == "the answer is 5"


def test_inner_and_outer_spokes_are_plain_functions(tmp_path):
    session = Session()
    step = inner_spoke(
        "hi", session, builtin_tools(), model="m", transport=_scripted_transport()
    )
    assert step["tool_calls"][0]["name"] == "add"
    # tool result was fed back into the session
    assert any(m.get("role") == "tool" for m in session.messages)
    idx = outer_spoke(Log(tmp_path / "l.jsonl"), step, session=session)
    assert idx == 0


def test_run_stops_at_max_turns(tmp_path):
    def always_tool(payload):
        return {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "x",
                                "type": "function",
                                "function": {"name": "echo", "arguments": '{"text": "y"}'},
                            }
                        ],
                    }
                }
            ],
            "usage": {},
        }

    result = run(
        "loop",
        model="m",
        tools=builtin_tools(),
        log_path=tmp_path / "log.jsonl",
        max_turns=3,
        transport=always_tool,
    )
    assert result["final_response"] is None
    assert result["log_length"] == 3
