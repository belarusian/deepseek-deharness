# TICKET-077 — inversion: plain function, not a plugin

## Capability
Preserve the deepseek-harness → deepseek-deharness inversion for the multi-run summary.

## Inversion check
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| summary plugin / profile-composed per-log entry-count view | `summary.batch_summary()` (one function composing batch_rollout + a per-log entry count over summarize_log) |
| summary composed by a bundle + DI wiring | `__main__.py --summary LOG [LOG ...]` flag |

## Constraints
- Plain functions, no plugin layer, no DI, no composition.
- The multi-run family now forms an eight-rung composition ladder: summarize (rollup) →
  aggregate (+outcome) → rollup (+size) → batch (+health) → manifest (+presence) →
  ledger (+tool-calls-per-log) → rollout (+final-response-len-per-log) → summary
  (+entries-per-log). Each layer reuses the one below it and adds exactly one new
  per-log dimension.
