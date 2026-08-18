# TICKET-065 — CLI --ledger LOG [LOG ...] flag

## Capability
Add a `--ledger LOG [LOG ...]` flag (nargs="+") to
`deepseek_deharness/__main__.py`. When given, it prints one line per rollup
field (runs / all_healthy=yes|no / total_entries / max_estimated_tokens /
identical_all=yes|no / tool_calls_total) plus one line per log:

    log <i>: healthy=yes|no final_response=<value or -> estimated_tokens=.. has_final_response=yes|no tool_calls=..

and exits 0 if all_healthy else 1. It calls `ledger.batch_ledger(args.ledger)`.

## File paths / signatures
- `deepseek_deharness/__main__.py` (additive only)
  - new `parser.add_argument("--ledger", metavar="LOG", nargs="+", type=str,
    default=None, help=...)` placed after the existing `--manifest` argument.
  - new `if args.ledger is not None:` handling block that mirrors the
    `--manifest` block but appends `tool_calls={n}` to each per-log line (zipping
    healthy_per_log / final_responses / estimated_tokens_per_log /
    has_final_response_per_log / tool_calls_per_log).

## Acceptance tests
- Existing flags (--replay/--verify/--inspect/--trace/--compact/--budget/
  --audit/--compare/--summarize/--aggregate/--rollup/--batch/--manifest) keep
  their exact behavior (regression-checked by the existing suite).
- `--ledger` over two healthy identical logs prints the six rollup lines and one
  per-log line each, exit 0; over a pair with a corrupt log it exits 1.

## Inversion
A plain argparse flag + print block — no plugin command registry.
