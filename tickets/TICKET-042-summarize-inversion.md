# TICKET-042 — inversion: a plain rollup function, not a plugin

## Capability
Preserve the deepseek-deharness inversion for this cycle's capability. Where
deepseek-harness (dsh) would express "roll up N runs into one report" as a
profile-composed bundle of plugins (a multi-run aggregation plugin wired through
the DI container), deepseek-deharness expresses it as ONE plain function:

    summarize_runs(paths) -> dict

...that calls the two existing plain functions (`audit.audit_log`,
`compare.compare_logs`) in a loop. No plugin layer, no DI, no composition
machinery — just a function over a list of paths.

## Acceptance
- `summarize.py` contains no imports beyond stdlib + the two sibling modules it
  composes; no class, no registry, no container.
- The diff vs main is additive only: no existing public signature changed.
