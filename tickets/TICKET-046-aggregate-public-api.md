# TICKET-046 — export aggregate_runs from the package

## Capability
Additively export `aggregate_runs` from `deepseek_deharness/__init__.py`:
- Import it: `from .aggregate import aggregate_runs`.
- Add `"aggregate_runs"` to `__all__`, keeping the list sorted (ruff RUF022)
  and the import block sorted (ruff I001).

## Rules
- Additive only: do NOT remove or reorder existing exports in a way that breaks
  them; keep everything else intact.
- No new dependencies.
