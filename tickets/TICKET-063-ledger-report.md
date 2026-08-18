# TICKET-063 — batch_ledger: multi-run ledger with per-log tool-call count

## Capability
New module `deepseek_deharness/ledger.py` exposing one plain function:

    batch_ledger(paths) -> dict

A read-only multi-run *ledger* that composes the existing manifest view with
per-log *tool-call count* detail into one view. Takes an iterable of log paths
and returns a dict with these keys:

- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`,
  `identical_all`, `final_responses`, `tool_calls_total`,
  `estimated_tokens_per_log`, `healthy_per_log`,
  `has_final_response_per_log` — taken **directly** from
  `manifest.batch_manifest(paths)` (reuse it; do NOT re-derive any of them).
- `tool_calls_per_log` — `[len(inspect.summarize_log(p)["tool_calls"]) for p in
  paths]`, a list of `int` aligned with the input order (one per log — that
  log's tool-call count).

## File paths / signatures
- `deepseek_deharness/ledger.py` (new)
  - `def batch_ledger(paths: list[str | Path] | tuple[str | Path, ...]) -> dict:`
  - stdlib only (`pathlib`). Reuse `manifest.batch_manifest` and
    `inspect.summarize_log`; do not re-implement either. Must not mutate any log
    file (read-only).

## Acceptance tests
Covered by TICKET-064 (`tests/test_ledger.py`). The function must:
- return all ten manifest keys unchanged from `batch_manifest(paths)`;
- add `tool_calls_per_log` as an int list aligned to input order;
- never write to or mutate any log file.

## Inversion
Plain function, no plugin layer, no DI, no composition object — the inverse of a
dsh ledger/profile bundle that would compose a per-log tool-call-count view.
