# TICKET-082 — inversion: plain function, not a plugin

## Capability
Confirm the detail capability is delivered as ONE plain function (`detail.batch_detail`) plus one
CLI flag, with no plugin layer, no DI, no composition machinery.

## Inversion (dsh -> deepseek-deharness)
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| detail plugin / profile-composed per-log message-count view | `detail.batch_detail()` (one function composing batch_summary + a per-log message count over summarize_log) |
| detail composed by a bundle + DI wiring | `__main__.py --detail LOG [LOG ...]` flag |

## Constraints
- stdlib only. No new dependencies. No plugin/DI/composition layer introduced.
