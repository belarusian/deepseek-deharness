# TICKET-037 — inversion: compare_logs is a plain function, not a plugin

## Capability
Preserve the deepseek-deharness inversion for Cycle 13's side-by-side log
comparison. Where deepseek-harness (dsh) would express "compare two runs" as a
Cordis plugin / profile-composed report, deepseek-deharness expresses it as ONE
plain function `compare_logs` that calls two existing plain functions
(`audit.audit_log`, `inspect.diff_logs`) and returns a dict.

## Rules (invariants)
- Plain functions only: no plugin layer, no DI, no composition machinery.
- Public API of existing modules never changes; new capability is a NEW module
  (`compare.py`) + a NEW CLI flag.
- stdlib only (json, pathlib, argparse). No new dependencies.
- `git diff main` must be ADDITIVE ONLY — no existing public signature changed.
