"""Tests for token-budget planning (budget.py).

Prove fits_budget is a correct budget check, plan_compaction returns a consistent
(max_messages, fits_after, estimated_tokens_after) triple that actually fits when
claimed, and that neither function mutates the original log.
"""
from __future__ import annotations

from deepseek_deharness.budget import fits_budget, plan_compaction
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


def test_fits_budget_generous_and_tiny(tmp_path):
    log_path = _run_to_log(tmp_path)
    est = estimate_tokens(log_path)
    assert est > 0
    # Generous budget fits; a tiny one does not.
    assert fits_budget(log_path, max_tokens=est * 10) is True
    assert fits_budget(log_path, max_tokens=0) is False


def test_plan_compaction_consistent_and_fits(tmp_path):
    log_path = _run_to_log(tmp_path)
    est = estimate_tokens(log_path)
    # Pick a budget below the full size so compaction is actually required.
    plan = plan_compaction(log_path, max_tokens=est // 2)
    assert plan["max_messages"] >= 0
    assert isinstance(plan["fits_after"], bool)
    assert plan["estimated_tokens_after"] >= 0

    # Recompute the estimate on a fresh compacted copy at the planned m to confirm.
    result = compact_log(log_path, max_messages=plan["max_messages"])
    recomputed = estimate_tokens(result["path"])
    assert recomputed == plan["estimated_tokens_after"]
    # fits_after must agree with the recomputed estimate vs the budget.
    assert plan["fits_after"] is (recomputed <= est // 2)


def test_plan_compaction_never_mutates_original(tmp_path):
    log_path = _run_to_log(tmp_path)
    before = log_path.read_bytes()
    fits_budget(log_path, max_tokens=10**9)
    plan_compaction(log_path, max_tokens=1)
    after = log_path.read_bytes()
    assert before == after


def test_empty_and_missing_log(tmp_path):
    missing = tmp_path / "nope.jsonl"
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")

    for path in (missing, empty):
        assert fits_budget(path, max_tokens=0) is True
        plan = plan_compaction(path, max_tokens=0)
        assert plan["max_messages"] == 0
        assert plan["estimated_tokens_after"] == 0
        assert plan["fits_after"] is True


def test_plan_compaction_zero_budget_still_reports(tmp_path):
    log_path = _run_to_log(tmp_path)
    # A zero budget: even m=0 (steps only) exceeds it, so fits_after must be False.
    plan = plan_compaction(log_path, max_tokens=0)
    assert plan["max_messages"] == 0
    assert plan["fits_after"] is False
    assert plan["estimated_tokens_after"] > 0
