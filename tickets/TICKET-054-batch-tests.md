# TICKET-054 — tests/test_batch.py for batch_report

## Capability
New test module `tests/test_batch.py` proving `batch.batch_report` composes
`rollup_runs` + `audit_log` into one consistent view with per-log health detail,
reports health/identity/outcome/size/health-per-log correctly across a batch,
and never mutates any input log.

## File paths / signatures
- `tests/test_batch.py` (new)
- Import `batch_report` from `deepseek_deharness.batch`; reuse the scripted
  transport + `_run_to_log` helpers pattern from `tests/test_rollup.py`.

## Acceptance tests (at least these four)
(a) **Two byte-identical healthy logs** → `runs=2`, `all_healthy=True`,
    `identical_all=True`, `total_entries == 2 * one log's entries`,
    `max_estimated_tokens > 0`, `final_responses` length 2 both equal and
    non-None, `tool_calls_total == 2 * one log's tool-call count`,
    `estimated_tokens_per_log` length 2 (both > 0), and
    `healthy_per_log == [True, True]`.
(b) **A pair where one log is corrupted** (corrupt side is the second log) →
    `all_healthy=False` and `identical_all=False`, while `final_responses` still
    has length 2, `estimated_tokens_per_log` still has length 2, and
    `healthy_per_log == [True, False]`.
(c) **Never mutates any input log** — all byte-identical before/after.
(d) **Empty path list** → `runs=0`, `all_healthy=True`, `total_entries=0`,
    `max_estimated_tokens=0`, `identical_all=True`, `final_responses=[]`,
    `tool_calls_total=0`, `estimated_tokens_per_log=[]`, `healthy_per_log=[]`.

## Inversion
Tests assert plain-function behavior (dict in / dict out, no mutation), not a
plugin/profile API.
