# TICKET-051 — export rollup_runs from the package

## Capability
Add an additive export of `rollup_runs` to `deepseek_deharness/__init__.py`:
import it from `.rollup` and add `"rollup_runs"` to `__all__`.

## Rules
- Additive only: do NOT remove or reorder existing exports in a way that breaks
  the public API. Keep imports and `__all__` sorted to satisfy ruff I001/RUF022.
- No new dependencies.
