# TICKET-024 — plan_compaction: largest per-entry message count that fits a budget

## Capability
`deepseek_deharness/budget.py`: `plan_compaction(log_path, max_tokens) -> dict` returning
`{max_messages: int, fits_after: bool, estimated_tokens_after: int}`. `max_messages` is the largest
integer m in [0..len(messages of first entry)] such that compacting to m messages per entry yields an
estimate <= max_tokens (binary search over m). If even m=0 exceeds budget, return max_messages=0 and
fits_after=False. Reuse `compact.compact_log` + `compact.estimate_tokens`; must not mutate the log.

## Acceptance
- Returns a non-negative max_messages with consistent fits_after/estimated_tokens_after (recompute
  estimate_tokens on the compacted temp file to confirm).
- Empty/missing log → max_messages=0, estimated_tokens_after=0, fits_after=True.
