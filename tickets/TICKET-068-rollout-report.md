# TICKET-068 — batch_rollout multi-run rollout (rollout.py)

## Capability
New module `deepseek_deharness/rollout.py` with one plain function:

    batch_rollout(paths) -> dict

A read-only multi-run *rollout* that composes the existing ledger view
(`ledger.batch_ledger`) with per-log *final-response length* detail into one view.

## Signature
```python
def batch_rollout(paths: list[str | Path] | tuple[str | Path, ...]) -> dict: ...
```

## Return shape
Returns a dict with these 12 keys:
- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`, `identical_all`,
  `final_responses`, `tool_calls_total`, `estimated_tokens_per_log`,
  `healthy_per_log`, `has_final_response_per_log`, `tool_calls_per_log` — all taken
  **directly** from `ledger.batch_ledger(paths)` (reuse it; do NOT re-derive).
- `final_response_len_per_log` : `list[int]` —
  `[len(fr) if fr is not None else 0 for fr in report["final_responses"]]`, aligned
  with the input order (one per log; that log's final-response character length, 0 when
  it produced no final response).

## Constraints
- Reuse `ledger.batch_ledger` (do not re-implement its logic).
- stdlib only (`json`, `pathlib`, `argparse`). No new dependencies.
- Must NOT mutate any log file.
- Plain function, no plugin layer, no DI, no composition machinery (the inversion).

## Acceptance
See TICKET-069 for the test suite that pins this behavior.
