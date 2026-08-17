"""Unit tests for the Session dataclass (plain, no inheritance)."""
from __future__ import annotations

from deepseek_deharness.session import Session


def test_append_and_reset():
    s = Session()
    s.append({"role": "user", "content": "hi"})
    s.append({"role": "assistant", "content": "hello"})
    assert len(s.messages) == 2
    s.reset()
    assert s.messages == []


def test_context_and_metadata_persist_across_reset():
    s = Session(context={"cwd": "/tmp"}, metadata={"id": "abc"})
    s.append({"role": "user", "content": "x"})
    s.reset()
    assert s.context == {"cwd": "/tmp"}
    assert s.metadata == {"id": "abc"}


def test_serialization_round_trip():
    s = Session(
        messages=[{"role": "user", "content": "hi"}],
        context={"k": 1},
        metadata={"m": "v"},
    )
    data = s.to_dict()
    s2 = Session.from_dict(data)
    assert s2.to_dict() == data
    # to_dict returns copies, not the live lists
    data["messages"].append({"role": "user", "content": "mut"})
    assert len(s.messages) == 1
