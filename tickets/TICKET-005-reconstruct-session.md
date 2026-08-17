# TICKET-005: reconstruct_session — rebuild a Session from the append-only log

**Status:** DONE (Cycle 3, commit da8cd91)

## What
`deepseek_deharness/replay.py::reconstruct_session(log_path) -> Session`
rebuilds a `Session` from the LAST entry's `messages`. The log is append-only
and each entry records the full conversation at that point, so the final entry
holds the complete state. An empty or missing log returns an empty `Session()`.

## Evidence
- `deepseek_deharness/replay.py:39` — takes `entries[-1]["messages"]`.
- `tests/test_replay.py::test_reconstruct_session_recovers_final_messages`
  asserts the recovered messages equal the original run's final messages.

## Impact (before)
No way to recover a session from a log; the "log is source of truth" decision
was not load-bearing.

## Suggestion / Resolution
Implemented as a plain function (no plugin, no DI). Verified by test.
