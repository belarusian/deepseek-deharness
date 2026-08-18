# TICKET-081 — export batch_detail (public API)

## Capability
Additively export `batch_detail` from `deepseek_deharness/__init__.py`.

## Constraints
- Add `from .detail import batch_detail` and add `"batch_detail"` to `__all__`.
- Keep imports and `__all__` sorted (ruff I001 / RUF022).
- Do NOT change any existing export or signature.
