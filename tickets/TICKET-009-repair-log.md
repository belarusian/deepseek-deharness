# TICKET-009: repair_log — drop trailing corrupt entries only

**Status:** DONE (Cycle 4)

## What
`deepseek_deharness/repair.py::repair_log(log_path) -> dict` drops only the
trailing run of corrupt entries (entries that fail to parse as JSON or lack the
`step`/`messages` keys) and returns `{repaired: bool, dropped: int,
entries_after: int}`. Healthy entries are preserved byte-for-byte; a log with no
trailing corruption is a no-op (`{repaired: False, dropped: 0}`).

## Evidence
- `deepseek_deharness/repair.py::repair_log` — finds the first trailing corrupt
  index and rewrites only the healthy prefix.
- `tests/test_repair.py::test_truncated_final_line_detected_and_repaired` — drops
  1, keeps 2, verifies clean after repair.
- `tests/test_repair.py::test_repair_drops_multiple_trailing_corrupt_entries` —
  drops 2 trailing corrupt lines.
- `tests/test_repair.py::test_repair_healthy_log_is_noop` — no-op on healthy log.

## Impact (before)
A truncated final line (interrupted write) left the log unreadable by
`reconstruct_session`/`replay`.

## Suggestion / Resolution
Implemented; stdlib only, plain function, does not mutate healthy entries.
