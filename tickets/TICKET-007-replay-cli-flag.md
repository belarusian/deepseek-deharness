# TICKET-007: CLI --replay LOG flag (existing flags unchanged)

**Status:** DONE (Cycle 3, commit da8cd91)

## What
`deepseek_deharness/__main__.py` gains a `--replay LOG` flag. When present the
CLI calls `replay(LOG)` instead of running a fresh harness and prints the
recovered final response. Existing flags (`goal`, `--model`, `--system`,
`--log`, `--max-turns`) and the fresh-run path are unchanged.

## Evidence
- `deepseek_deharness/__main__.py:27` — new `--replay` argument (default None).
- `deepseek_deharness/__main__.py:36` — `if args.replay is not None:` branch.
- `git diff main -- deepseek_deharness/__main__.py` shows only additive lines.

## Impact (before)
No CLI way to replay a run from its log.

## Suggestion / Resolution
Implemented; verified end-to-end via subprocess (recovers "the answer is 5"
with no LLM reachable).
