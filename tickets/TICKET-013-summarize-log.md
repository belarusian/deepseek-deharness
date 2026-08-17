# TICKET-013: summarize_log — read-only human summary of an append-only log

**Status:** OPEN (Cycle 5)

## What
`deepseek_deharness/inspect.py::summarize_log(log_path) -> dict` returns a
read-only, human-readable summary of an append-only log. Keys:
- `entries`: int — number of log entries.
- `message_count`: int — length of the LAST entry's `messages` (0 if no entries).
- `roles`: dict[str, int] — count of each message role across the LAST entry's messages.
- `tool_calls`: list[dict] — for every tool call seen in any entry's `step`, a record
  `{index: <entry index>, name: <tool name>}` (in log order).
- `final_response`: str | None — last assistant content in the LAST entry's messages.
- `healthy`: bool — `verify_log(log_path) == []`.

Must NOT mutate the log file (byte-identical before/after). Stdlib only (json, pathlib).

## Evidence
- `deepseek_deharness/inspect.py::summarize_log` — new plain function.
- `tests/test_inspect.py::test_summarize_healthy_scripted_run` — correct fields + healthy=True.
- `tests/test_inspect.py::test_summarize_truncated_log` — healthy=False, recoverable fields.
- `tests/test_inspect.py::test_summarize_never_mutates_log` — byte-identical before/after.

## Impact (before)
No way to see what's in a log at a glance; the source of truth was auditable (C4)
but not inspectable.

## Suggestion / Resolution
Implement as a plain stdlib function; reuse `repair.verify_log` for `healthy`.
