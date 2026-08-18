# TICKET-025 — tests/test_budget.py

## Capability
`tests/test_budget.py`: (a) fits_budget True for a generous budget and False for a tiny one on a real
two-turn log; (b) plan_compaction returns a non-negative max_messages and a consistent
fits_after/estimated_tokens_after (recompute estimate_tokens on the compacted temp file to confirm);
(c) both functions never mutate the original log (byte-identical before/after); (d) an empty/missing
log yields fits_budget=True and plan_compaction with max_messages=0, estimated_tokens_after=0.

## Acceptance
- All four behaviors covered; `python3 -m pytest -q` green.
