# TICKET-030 — CLI: --audit LOG flag in __main__.py

## Capability
`deepseek_deharness/__main__.py`: add a `--audit LOG` flag. When given, call
`audit.audit_log(LOG)` and print one line per field:
  entries=... / healthy=yes|no / violations=<count> / final_response=... / tool_calls=... /
  estimated_tokens=...
Exit 0 if healthy else 1. Do NOT change the behavior of any existing flag
(--replay/--verify/--inspect/--trace/--compact/--budget). Additive only: import audit_log, add the
argparse option and its dispatch branch.

## Acceptance
- `python -m deepseek_deharness "goal" --audit <healthy-log>` prints all six fields and exits 0.
- `python -m deepseek_deharness "goal" --audit <corrupt-log>` prints all six fields and exits 1.
- Existing flags unchanged (regression: --inspect/--verify/--trace/--compact/--budget still work).
