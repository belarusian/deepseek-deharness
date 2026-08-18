# TICKET-041 — export summarize_runs in the public API

## Capability
Additively export `summarize_runs` from `deepseek_deharness/__init__.py`:
- add `from .summarize import summarize_runs` to the import block (kept sorted
  to satisfy ruff I001/RUF022), and
- add `"summarize_runs"` to `__all__` (kept sorted).

## Constraints
- Purely additive: no existing import, export, or public signature changes.
- `python3 -m mypy deepseek_deharness/` and `python3 -m ruff check .` stay green.

## Acceptance
`from deepseek_deharness import summarize_runs` works; gate (pytest/ruff/mypy)
green.
