# TICKET-070 — CLI --rollout LOG [LOG ...] flag

## Capability
Add a `--rollout LOG [LOG ...]` flag (nargs="+") to `deepseek_deharness/__main__.py`.

## Behavior
Print one line per rollup field:
    runs / all_healthy=yes|no / total_entries / max_estimated_tokens /
    identical_all=yes|no / tool_calls_total
plus one line per log:
    log <i>: healthy=yes|no final_response=<value or -> estimated_tokens=..
             has_final_response=yes|no tool_calls=.. final_response_len=..
Exit 0 if all_healthy else 1.

## Constraints
- Do NOT change existing flags' behavior (including --replay/--verify/--inspect/
  --trace/--compact/--budget/--audit/--compare/--summarize/--aggregate/--rollup/
  --batch/--manifest/--ledger).
- Additive only: new flag + handler; no existing public signature changed.
