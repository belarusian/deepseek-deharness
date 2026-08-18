# TICKET-053 — batch_report: multi-run report with per-log health detail

## Capability
New module `deepseek_deharness/batch.py` exposing one plain function:

    batch_report(paths) -> dict

A read-only multi-run report that composes the existing rollup view with
per-log *health* detail into one view. Takes an iterable of log paths and
returns a dict with these keys:

- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`,
  `identical_all`, `final_responses`, `tool_calls_total`,
  `estimated_tokens_per_log` — taken **directly** from
  `rollup.rollup_runs(paths)` (reuse it; do NOT re-derive any of them).
- `healthy_per_log` — `[audit.audit_log(p)["healthy"] for p in paths]`, a list
  of `bool` aligned with the input order (one per log).

## File paths / signatures
- `deepseek_deharness/batch.py` (new)
  - `def batch_report(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:`
  - stdlib only (`pathlib`). Reuse `rollup.rollup_runs` and `audit.audit_log`;
    do not re-implement either. Must not mutate any log file (read-only).

## Acceptance tests
Covered by TICKET-054 (`tests/test_batch.py`). The function must:
- return all eight rollup keys unchanged from `rollup_runs(paths)`;
- add `healthy_per_log` as a bool list aligned to input order;
- never write to or mutate any log file.

## Inversion
Plain function, no plugin layer, no DI, no composition object — the inverse of
a dsh batch-report plugin/profile bundle.
