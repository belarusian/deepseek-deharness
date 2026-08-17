# TICKET-017: export summarize_log + diff_logs from the package

**Status:** OPEN (Cycle 5)

## What
`deepseek_deharness/__init__.py` exports `summarize_log` and `diff_logs` from
`.inspect` (additive import + `__all__` entries). No existing export is removed or
re-signatured.

## Evidence
- `deepseek_deharness/__init__.py` — `from .inspect import diff_logs, summarize_log`
  plus both names in `__all__`.
- `python -c "import deepseek_deharness as d; d.summarize_log; d.diff_logs"` succeeds.

## Impact (before)
The new inspect functions would not be part of the public API.

## Suggestion / Resolution
Additive import + __all__ entries only.
