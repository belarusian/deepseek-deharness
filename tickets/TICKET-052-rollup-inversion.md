# TICKET-052 — inversion: rollup_runs is a plain function, not a plugin

## Capability
Confirm the inversion holds for Cycle 16: where deepseek-harness (dsh) would
express a multi-run report with per-log size detail as a profile-composed batch
report plugin wired through DI/bundles, deepseek-deharness expresses it as ONE
plain function `rollup.rollup_runs()` that composes two existing plain functions
(`aggregate.aggregate_runs` + `audit.audit_log`) and is surfaced by a flat
argparse flag (`__main__.py --rollup`).

## Rules
- No plugin layer, no DI container, no composition machinery.
- The change must be additive: `git diff main` shows no modified public signature
  in any existing module (only new module + new flag + new export).
