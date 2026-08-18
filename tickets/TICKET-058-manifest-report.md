# TICKET-058 — batch_manifest: multi-run manifest with per-log final-response presence

## Capability
New module `deepseek_deharness/manifest.py` exposing one plain function:

    batch_manifest(paths) -> dict

A read-only multi-run *manifest* that composes the existing batch view with
per-log *final-response presence* detail into one view. Takes an iterable of
log paths and returns a dict with these keys:

- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`,
  `identical_all`, `final_responses`, `tool_calls_total`,
  `estimated_tokens_per_log`, `healthy_per_log` — taken **directly** from
  `batch.batch_report(paths)` (reuse it; do NOT re-derive any of them).
- `has_final_response_per_log` — `[fr is not None for fr in
  batch_report(paths)["final_responses"]]`, a list of `bool` aligned with the
  input order (one per log; True iff that log produced a non-None final
  assistant response).

## File paths / signatures
- `deepseek_deharness/manifest.py` (new)
  - `def batch_manifest(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:`
  - stdlib only (`pathlib`). Reuse `batch.batch_report`; do not re-implement it.
    Must not mutate any log file (read-only).

## Acceptance tests
Covered by TICKET-059 (`tests/test_manifest.py`). The function must:
- return all nine batch keys unchanged from `batch_report(paths)`;
- add `has_final_response_per_log` as a bool list aligned to input order;
- never write to or mutate any log file.

## Inversion
Plain function, no plugin layer, no DI, no composition object — the inverse of
a dsh batch-manifest plugin/profile bundle.
