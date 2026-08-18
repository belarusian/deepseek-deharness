# TICKET-031 — export audit_log from the package public API

## Capability
`deepseek_deharness/__init__.py`: additively export `audit_log` (import from `.audit`) and add it to
`__all__`. Keep `__all__` sorted to satisfy ruff RUF022. Do not change any existing export or
signature.

## Acceptance
- `from deepseek_deharness import audit_log` works.
- `"audit_log" in deepseek_deharness.__all__`.
- `python3 -m ruff check .` reports zero issues (RUF022 sort order preserved).
