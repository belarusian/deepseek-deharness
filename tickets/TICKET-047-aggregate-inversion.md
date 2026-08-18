# TICKET-047 — inversion: aggregate_runs is a plain function, not a plugin

## Capability
Preserve the deepseek-harness → deepseek-deharness inversion for this cycle's
new capability.

| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| multi-run aggregation plugin / profile-composed batch report with per-log detail | `aggregate.aggregate_runs()` (one function composing summarize_runs + summarize_log) |
| batch rollup composed by a bundle + DI wiring | `__main__.py --aggregate LOG [LOG ...]` flag |

## Rules
- Plain functions only: no plugin layer, no DI container, no composition root.
- `aggregate.py` must import and call the existing plain functions
  (`summarize.summarize_runs`, `inspect.summarize_log`) — not re-implement them.
- The CLI flag is a flat argparse branch in `__main__.py`.
