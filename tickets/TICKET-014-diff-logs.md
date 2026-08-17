# TICKET-014: diff_logs — pairwise log comparison / fork-point detection

**Status:** OPEN (Cycle 5)

## What
`deepseek_deharness/inspect.py::diff_logs(a_path, b_path) -> dict` compares two
append-only logs. Keys:
- `a_entries`: int, `b_entries`: int — entry counts.
- `common_prefix`: int — number of leading entries that are byte-identical (same JSON line).
- `divergent_at`: int | None — first index at which the two logs differ; None if one is a
  prefix of the other or they are identical.

Stdlib only (json, pathlib). Read-only: must not mutate either log.

## Evidence
- `deepseek_deharness/inspect.py::diff_logs` — new plain function.
- `tests/test_inspect.py::test_diff_identical_logs` — common_prefix == len, divergent_at None.
- `tests/test_inspect.py::test_diff_shared_prefix_then_diverge` — correct prefix + index.

## Impact (before)
No way to detect where two runs forked; the append-only log's replayability had no
pairwise tooling.

## Suggestion / Resolution
Implement as a plain stdlib function comparing raw JSON lines.
