# TICKET-049 — tests/test_rollup.py for rollup_runs

## Capability
New test module `tests/test_rollup.py` proving `rollup_runs` composes
`aggregate_runs` + `audit_log` into one consistent view with per-log size detail,
reports health/identity/outcome/size correctly across a batch, and never mutates
any input log.

## Acceptance tests
- (a) On two byte-identical healthy logs: runs=2, all_healthy=True,
  identical_all=True, total_entries = 2x one log's entries,
  max_estimated_tokens > 0, final_responses has length 2 with both entries equal
  and non-None, tool_calls_total = 2x one log's tool-call count, and
  estimated_tokens_per_log has length 2 with both entries equal to that log's
  audit estimated_tokens (> 0).
- (b) On a pair where one log is corrupted: all_healthy=False and
  identical_all=False while final_responses still has length 2 and
  estimated_tokens_per_log still has length 2.
- (c) rollup_runs never mutates any input log (all byte-identical before/after).
- (d) An empty path list yields runs=0, all_healthy=True, total_entries=0,
  max_estimated_tokens=0, identical_all=True, final_responses=[],
  tool_calls_total=0, estimated_tokens_per_log=[].

## Rules
- stdlib only. Reuse the existing test helpers (scripted transport + run).
