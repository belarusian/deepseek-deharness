# TICKET-076 — export batch_summary (public API)

## Capability
Export `batch_summary` from the package public API in
`deepseek_deharness/__init__.py`.

## Change
- Add `from .summary import batch_summary` to the imports.
- Add `"batch_summary"` to `__all__`.
- Keep imports and `__all__` sorted to satisfy ruff I001/RUF022.

## Constraints
- Additive only: no existing export removed or renamed.
