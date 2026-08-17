# TICKET-008: verify_log — audit the append-only log's invariants

**Status:** DONE (Cycle 4)

## What
`deepseek_deharness/repair.py::verify_log(log_path) -> list[dict]` checks the
append-only log's invariants and returns one violation record per problem found
(empty list = healthy). Invariants: (1) every entry has a `step` dict and a
`messages` list; (2) `messages` length is monotonically non-decreasing across
entries; (3) each entry's `messages` extends the previous entry's by prefix. A
line that is not valid JSON is reported as a `bad_json` violation.

## Evidence
- `deepseek_deharness/repair.py::verify_log` — three invariant checks + bad_json.
- `tests/test_repair.py::test_healthy_log_verifies_clean` — real scripted run → [].
- `tests/test_repair.py::test_mid_conversation_mutation_flagged` — prefix_violation.
- `tests/test_repair.py::test_messages_shrink_flagged` — messages_shrank.

## Impact (before)
A corrupted or mutated log could not be detected; the "source of truth" was
unauditable.

## Suggestion / Resolution
Implemented; stdlib only, plain function, no plugin layer.
