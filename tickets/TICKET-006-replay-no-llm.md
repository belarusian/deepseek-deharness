# TICKET-006: replay — pure re-read path must never call the LLM

**Status:** DONE (Cycle 3, commit da8cd91)

## What
`deepseek_deharness/replay.py::replay(log_path, *, transport=None, max_turns=8)`
with `transport is None` is a pure "re-read the log" path: it returns the
recovered `final_response` and `message_count` without touching any LLM. With a
transport it continues remaining turns via the four algebra (inner/outer spoke),
reconciling each new turn into the same append-only log.

## Evidence
- `deepseek_deharness/replay.py:63` — `if transport is None:` returns early.
- `tests/test_replay.py::test_replay_without_transport_does_not_call_llm`
  asserts the recovered final response matches and no new log entry is appended.
- `tests/test_replay.py::test_replay_with_transport_continues_from_recovered_state`
  proves continuation appends a new reconciled entry (log_length 1 -> 2).

## Impact (before)
A finished run could not be replayed from its log alone.

## Suggestion / Resolution
Implemented; both the no-LLM and continuation paths are tested.
