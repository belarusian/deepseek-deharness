# TICKET-039 — tests/test_summarize.py

## Capability
New test module `tests/test_summarize.py` proving `summarize_runs` composes the
per-log views correctly and never mutates its inputs.

## Required tests
(a) On two byte-identical healthy logs: `runs == 2`, `all_healthy is True`,
    `identical_all is True`, `total_entries == 2 * (one log's entries)`,
    `max_estimated_tokens > 0`.
(b) On a pair where one log is corrupted (unhealthy): `all_healthy is False` and
    `identical_all is False`, while the per-log `logs` list still holds both full
    reports (each with populated entries/healthy fields).
(c) `summarize_runs` never mutates any input log: every input file is
    byte-identical before and after the call.
(d) An empty path list yields `runs == 0`, `logs == []`, `all_healthy is True`,
    `total_entries == 0`, `max_estimated_tokens == 0`, `identical_all is True`.

## Acceptance
`python3 -m pytest tests/test_summarize.py -q` passes; all four behaviors above
are asserted.
