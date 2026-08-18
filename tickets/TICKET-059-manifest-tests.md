# TICKET-059 — tests/test_manifest.py: batch_manifest behavior

## Capability
New test module `tests/test_manifest.py` proving `manifest.batch_manifest`
composes `batch.batch_report` into one consistent view with per-log
final-response presence detail, reports health/identity/outcome/size/health-per-log/
presence-per-log correctly across a manifest, and never mutates any input log.

## File paths / signatures
- `tests/test_manifest.py` (new) — plain pytest functions using `tmp_path`.

## Acceptance tests (each must pass)
(a) Two byte-identical healthy logs: `batch_manifest` reports runs=2,
    all_healthy=True, identical_all=True, total_entries = 2x one log's entries,
    max_estimated_tokens > 0, final_responses length 2 with both entries equal and
    non-None, tool_calls_total = 2x one log's tool-call count,
    estimated_tokens_per_log length 2 (both > 0), healthy_per_log == [True, True],
    and has_final_response_per_log == [True, True].
(b) A pair where the second log is corrupted: all_healthy=False and
    identical_all=False while final_responses still has length 2,
    estimated_tokens_per_log still has length 2, healthy_per_log == [True, False],
    and has_final_response_per_log reflects which logs produced a non-None final
    response (the corrupt side may be False).
(c) `batch_manifest` never mutates any input log (all byte-identical before/after).
(d) An empty path list yields runs=0, all_healthy=True, total_entries=0,
    max_estimated_tokens=0, identical_all=True, final_responses=[], tool_calls_total=0,
    estimated_tokens_per_log=[], healthy_per_log=[], has_final_response_per_log=[].
(e) A single log with no assistant content (final_response None):
    has_final_response_per_log == [False].

## Inversion
Plain pytest functions; no fixtures beyond `tmp_path`; no plugin machinery.
