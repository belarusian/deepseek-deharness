# TICKET-071 — export batch_rollout (public API)

## Capability
Additively export `batch_rollout` from `deepseek_deharness/__init__.py`.

## Constraints
- Add `from .rollout import batch_rollout` and add `"batch_rollout"` to `__all__`.
- Keep imports and `__all__` sorted to satisfy ruff I001/RUF022.
- Do NOT change any existing export or signature (additive only).
