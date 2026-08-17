# TICKET-016: CLI --inspect LOG flag (existing flags unchanged)

**Status:** OPEN (Cycle 5)

## What
`deepseek_deharness/__main__.py` gains a `--inspect LOG` flag. When present the
CLI prints a human-readable summary from `summarize_log(LOG)` (one line per key;
tool_calls as "idx name" lines) and exits 0. Existing flags (`goal`, `--model`,
`--system`, `--log`, `--max-turns`) and the Cycle 3 `--replay` / Cycle 4 `--verify`
flags are unchanged.

## Evidence
- `deepseek_deharness/__main__.py` — new `--inspect` argument (default None) and an
  `if args.inspect is not None:` branch.
- End-to-end: `python -m deepseek_deharness "goal" --inspect <healthy>` prints the
  summary, exit 0; `--replay`/`--verify` regression-checked.
- `git diff main -- deepseek_deharness/__main__.py` shows only additive lines.

## Impact (before)
No CLI way to inspect a log's contents at a glance.

## Suggestion / Resolution
Implement as an additive argparse flag + branch; do not touch existing branches.
