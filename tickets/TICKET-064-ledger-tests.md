# TICKET-064 — tests/test_ledger.py: batch_ledger behavior

## Capability
New test module `tests/test_ledger.py` proving `batch_ledger` composes
`manifest.batch_manifest` into one consistent view with per-log tool-call count
detail, reports health/identity/outcome/size/health-per-log/presence-per-log/
tool-calls-per-log correctly across a ledger, and never mutates any input log.

## File paths / signatures
- `tests/test_ledger.py` (new) — plain pytest functions using the same scripted
  transport + `run(...)` helper pattern as `tests/test_manifest.py`.

## Acceptance tests
- (a) two byte-identical healthy logs: runs=2, all_healthy=True,
  identical_all=True, total_entries = 2x one log's entries,
  max_estimated_tokens > 0, final_responses length 2 both equal and non-None,
  tool_calls_total = 2x one log's tool-call count, estimated_tokens_per_log
  length 2 (both > 0), healthy_per_log == [True, True],
  has_final_response_per_log == [True, True], and tool_calls_per_log == [n, n]
  where n is one log's tool-call count (> 0).
- (b) a pair where the second log is corrupted: all_healthy=False and
  identical_all=False while final_responses still has length 2,
  estimated_tokens_per_log still has length 2, healthy_per_log == [True, False],
  has_final_response_per_log consistent with final_responses, and
  tool_calls_per_log still has length 2 (the corrupt side's count reflects only
  its parseable entries).
- (c) batch_ledger never mutates any input log (all byte-identical before/after).
- (d) an empty path list yields runs=0, all_healthy=True, total_entries=0,
  max_estimated_tokens=0, identical_all=True, final_responses=[],
  tool_calls_total=0, estimated_tokens_per_log=[], healthy_per_log=[],
  has_final_response_per_log=[], tool_calls_per_log=[].
- (e) on a single log with no tool calls, tool_calls_per_log == [0].

## Inversion
Tests exercise one plain function end-to-end; no plugin harness or DI fixture.
