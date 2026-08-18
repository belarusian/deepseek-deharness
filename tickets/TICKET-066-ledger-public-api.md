# TICKET-066 — export batch_ledger from the package

## Capability
Export `batch_ledger` from `deepseek_deharness/__init__.py` so it is part of the
public API alongside `batch_manifest`.

## File paths / signatures
- `deepseek_deharness/__init__.py` (additive only)
  - add `from .ledger import batch_ledger` to the imports (kept sorted to satisfy
    ruff I001/RUF022 — `ledger` sorts after `inspect`/before `llm_adapter`).
  - add `"batch_ledger"` to `__all__` (kept sorted).

## Acceptance tests
- `from deepseek_deharness import batch_ledger` succeeds.
- `python3 -m ruff check .` reports zero issues (import + `__all__` ordering).
- No existing export is removed or reordered in a way that breaks the suite.

## Inversion
A single flat re-export — no plugin registration or capability manifest.
