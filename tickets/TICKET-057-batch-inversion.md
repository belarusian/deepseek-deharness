# TICKET-057 — inversion: batch_report is a plain function, not a plugin

## Capability
Guarantee the dsh → deepseek-deharness inversion holds for the new batch-report
capability: where deepseek-harness (dsh) would express a multi-run batch report
with per-log health detail as a composed plugin/profile bundle wired by DI,
deepseek-deharness expresses it as ONE plain function.

## File paths / signatures
- `deepseek_deharness/batch.py` — one module-level function `batch_report`; no
  class, no registry, no DI container, no composition object, no new dependency.
- The diff vs `main` must be **additive only**: no existing public signature is
  changed; `git diff main` shows insertions only (plus the two additive edits to
  `__init__.py` and `__main__.py`).

## Acceptance tests
- `deepseek_deharness/batch.py` contains exactly one public function and imports
  only stdlib + the existing `rollup`/`audit` modules.
- `git diff main -- deepseek_deharness/` shows no modified existing signature.
- Full gate green: pytest (count >= previous cycle), ruff, mypy.

## Inversion table (dsh → deepseek-deharness)
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| multi-run batch-report plugin / profile-composed report with per-log health detail | `batch.batch_report()` (one function composing rollup_runs + audit_log) |
| batch report composed by a bundle + DI wiring | `__main__.py --batch LOG [LOG ...]` flag |
