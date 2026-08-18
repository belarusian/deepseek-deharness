# TICKET-044 — tests/test_aggregate.py: prove aggregate_runs composes correctly

## Capability
New test file `tests/test_aggregate.py` exercising `aggregate.aggregate_runs`.

## Acceptance tests
(a) On two byte-identical healthy logs, aggregate_runs reports runs=2,
    all_healthy=True, identical_all=True, total_entries = 2x one log's entries,
    max_estimated_tokens > 0, final_responses has length 2 with both entries
    equal and non-None, and tool_calls_total = 2x one log's tool-call count.
(b) On a pair where one log is corrupted, all_healthy=False and
    identical_all=False while final_responses still has length 2 (one entry may
    be None for the corrupt side).
(c) aggregate_runs never mutates any input log (all byte-identical before/after).
(d) An empty path list yields runs=0, all_healthy=True, total_entries=0,
    max_estimated_tokens=0, identical_all=True, final_responses=[],
    tool_calls_total=0.

## Rules
- Use a scripted transport (as in tests/test_summarize.py) to produce real logs.
- stdlib only. No new dependencies.
