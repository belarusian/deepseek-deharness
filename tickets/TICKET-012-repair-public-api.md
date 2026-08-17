# TICKET-012: export verify_log + repair_log from the package

**Status:** DONE (Cycle 4)

## What
`deepseek_deharness/__init__.py` re-exports `verify_log` and `repair_log` from
the new `repair` module (additive; existing exports unchanged). Keeps the public
API flat — no plugin layer, no DI.

## Evidence
- `deepseek_deharness/__init__.py` — `from .repair import repair_log, verify_log`
  and both names added to `__all__`.
- `python3 -c "from deepseek_deharness import repair_log, verify_log"` succeeds.
- `git diff main -- deepseek_deharness/__init__.py` shows only additive lines.

## Impact (before)
The repair/verify functions were not part of the package's public surface.

## Suggestion / Resolution
Implemented; purely additive, no existing export removed or renamed.
