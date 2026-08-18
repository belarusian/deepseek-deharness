# TICKET-073 — batch_summary multi-run summary (summary.py)

## Capability
New module `deepseek_deharness/summary.py` with one plain function:

    batch_summary(paths) -> dict

A read-only multi-run *summary* that composes the existing rollout view
(`rollout.batch_rollout`) with per-log *entry count* detail into one view.

## Signature
```python
def batch_summary(paths: list[str | Path] | tuple[str | Path, ...]) -> dict: ...
```

## Return shape
Returns a dict with these 13 keys:
- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`, `identical_all`,
  `final_responses`, `tool_calls_total`, `estimated_tokens_per_log`,
  `healthy_per_log`, `has_final_response_per_log`, `tool_calls_per_log`,
  `final_response_len_per_log` — all taken **directly** from
  `rollout.batch_rollout(paths)` (reuse it; do NOT re-derive).
- `entries_per_log` : `list[int]` — `[summarize_log(p)["entries"] for p in paths]`,
  aligned with the input order (one per log; that log's entry count, an int).

## Constraints
- Reuse `rollout.batch_rollout` and `inspect.summarize_log` (do not re-implement their logic).
- stdlib only (`json`, `pathlib`, `argparse`). No new dependencies.
- Must NOT mutate any log file.
- Plain function, no plugin layer, no DI, no composition machinery (the inversion).

## Acceptance
See TICKET-074 for the test suite that pins this behavior.
