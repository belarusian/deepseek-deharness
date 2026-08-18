# TICKET-072 — inversion: plain function, not a plugin

## Capability
Preserve the deepseek-deharness inversion for the rollout capability.

## Inversion check (dsh -> deepseek-deharness)
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| rollout plugin / profile-composed per-log final-response-length view | `rollout.batch_rollout()` (one function composing batch_ledger + a per-log length over final_responses) |
| rollout composed by a bundle + DI wiring | `__main__.py --rollout LOG [LOG ...]` flag |

## Constraints
- Plain functions, no plugin layer, no DI, no composition.
- Existing core modules byte-identical; only `__main__.py` and `__init__.py` change,
  both purely additively. `git diff main` must be additive only (no modified public
  signature).
