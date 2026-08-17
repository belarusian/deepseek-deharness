"""Unit tests for the append-only Log (plain file-backed journal)."""
from __future__ import annotations

from deepseek_deharness.log import Log


def test_append_only_and_order(tmp_path):
    log = Log(tmp_path / "log.jsonl")
    i0 = log.append({"n": 0})
    i1 = log.append({"n": 1})
    assert (i0, i1) == (0, 1)
    assert log.read() == [{"n": 0}, {"n": 1}]
    assert len(log) == 2


def test_persists_across_instances(tmp_path):
    p = tmp_path / "log.jsonl"
    Log(p).append({"a": 1})
    log2 = Log(p)  # new instance, same file
    assert log2.read() == [{"a": 1}]
    log2.append({"b": 2})
    assert Log(p).read() == [{"a": 1}, {"b": 2}]
