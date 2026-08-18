# TICKET-056 — export batch_report in the public API

## Capability
Add `batch_report` to the package's public API so it is importable as
`from deepseek_deharness import batch_report`.

## File paths / signatures
- `deepseek_deharness/__init__.py` — additive only:
  - add `from .batch import batch_report` (keep imports sorted for ruff I001);
  - add `"batch_report"` to `__all__` (keep the list sorted for RUF022).

## Acceptance tests
- `python3 -c "from deepseek_deharness import batch_report"` succeeds.
- `python3 -m ruff check .` reports zero issues (import + `__all__` ordering).
- No existing export is removed or renamed.

## Inversion
A single name in a flat module's `__all__` — not a dsh plugin registry entry.
