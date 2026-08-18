# TICKET-032 — inversion: audit_log is a plain function, not a plugin

## Capability
Confirm the inversion holds for the new capability: where deepseek-harness (dsh) would express a
"health/audit report" as a composed Cordis plugin (a context-budget/verify/inspect plugin bundle),
deepseek-deharness expresses it as ONE plain function `audit_log` that calls three other plain
functions. No plugin layer, no DI container, no composition framework — just imports and a dict.

## Acceptance
- `audit.py` contains only plain functions (no classes, no registries, no decorators beyond stdlib).
- `git diff main` for the new/changed files is additive only: no existing public signature changed.
- Stdlib only (json, pathlib, argparse); no new dependencies.
