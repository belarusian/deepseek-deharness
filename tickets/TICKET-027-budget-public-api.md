# TICKET-027 — export budget functions from the package

## Capability
`deepseek_deharness/__init__.py`: additive export of `fits_budget` and `plan_compaction` (import from
`.budget`, add to `__all__`). Do NOT change any existing export or signature.

## Acceptance
- `from deepseek_deharness import fits_budget, plan_compaction` works; existing exports unchanged.
