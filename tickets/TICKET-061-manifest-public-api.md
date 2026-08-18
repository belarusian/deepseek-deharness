# TICKET-061 — export batch_manifest from the package

## Capability
Additively export `batch_manifest` from `deepseek_deharness/__init__.py` so the
new module is part of the public API, keeping imports and `__all__` sorted to
satisfy ruff (I001/RUF022).

## File paths / signatures
- `deepseek_deharness/__init__.py` (modified, additive only)
  - `from .manifest import batch_manifest`
  - `"batch_manifest",` added to `__all__` in sorted position.

## Constraints / acceptance
- No existing export removed or reordered out of sort order.
- `python3 -m ruff check .` reports zero issues; `python3 -m mypy deepseek_deharness/`
  reports zero issues.

## Inversion
A plain re-export, not a DI registration or plugin manifest entry.
