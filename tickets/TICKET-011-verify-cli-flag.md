# TICKET-011: CLI --verify LOG flag (existing flags unchanged)

**Status:** DONE (Cycle 4)

## What
`deepseek_deharness/__main__.py` gains a `--verify LOG` flag. When present the
CLI calls `verify_log(LOG)` and prints "OK" (exit 0) if healthy, or one line per
violation (exit 1). Existing flags (`goal`, `--model`, `--system`, `--log`,
`--max-turns`) and the Cycle 3 `--replay` flag are unchanged.

## Evidence
- `deepseek_deharness/__main__.py` — new `--verify` argument (default None) and
  an `if args.verify is not None:` branch placed before the replay branch.
- End-to-end: `python -m deepseek_deharness "goal" --verify <healthy>` → "OK",
  exit 0; on a truncated log → "[2] bad_json: ...", exit 1.
- `git diff main -- deepseek_deharness/__main__.py` shows only additive lines.

## Impact (before)
No CLI way to audit a log's integrity.

## Suggestion / Resolution
Implemented; verified end-to-end for both healthy and corrupt logs.
