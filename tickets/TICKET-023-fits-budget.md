# TICKET-023 — fits_budget: does a log fit a token budget?

## Capability
`deepseek_deharness/budget.py` (new module, stdlib only): `fits_budget(log_path, max_tokens) -> bool`.
True iff `compact.estimate_tokens(log_path) <= max_tokens`. MUST reuse `compact.estimate_tokens`
(import it; do not re-implement the heuristic). Must not mutate the log file.

## Acceptance
- On a real two-turn log: True for a generous budget, False for a tiny one.
- Empty/missing log → estimate is 0 → fits_budget is True for any max_tokens >= 0.
- Never mutates the original log (byte-identical before/after).
