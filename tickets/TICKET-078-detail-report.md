# TICKET-078 — batch_detail multi-run detail (detail.py)

## Capability
New module `deepseek_deharness/detail.py` with one plain function:

    batch_detail(paths) -> dict

A read-only multi-run *detail* that composes the existing summary view
(`summary.batch_summary`) with per-log *message count* detail into one view.

## Signature
```python
def batch_detail(paths: list[str | Path] | tuple[str | Path, ...]) -> dict: ...
```

## Return shape
Returns a dict with these 14 keys:
- `runs`, `all_healthy`, `total_entries`, `max_estimated_tokens`, `identical_all`,
  `final_responses`, `tool_calls_total`, `estimated_tokens_per_log`,
  `healthy_per_log`, `has_final_response_per_log`, `tool_calls_per_log`,
  `final_response_len_per_log`, `entries_per_log` — all taken **directly** from
  `summary.batch_summary(paths)` (reuse it; do NOT re-derive).
- `message_count_per_log` : `list[int]` — `[summarize_log(p)["message_count"] for p in paths]`,
  aligned with the input order (one per log; that log's message count: the length of its LAST
  entry's `messages`, 0 if none).

## Constraints
- Reuse `summary.batch_summary` and `inspect.summarize_log` (do not re-implement their logic).
- stdlib only (`json`, `pathlib`, `argparse`). No new dependencies.
- Must NOT mutate any log file.
- Plain function, no plugin layer, no DI, no composition machinery (the inversion).

## Acceptance
See TICKET-079 for the test suite that pins this behavior.
