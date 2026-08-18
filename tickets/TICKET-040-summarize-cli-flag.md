# TICKET-040 — CLI --summarize LOG [LOG ...] flag

## Capability
Add an additive `--summarize` flag to `deepseek_deharness/__main__.py`:

    parser.add_argument("--summarize", metavar="LOG", nargs="+", type=str, default=None)

When set, call `summarize_runs(args.summarize)` and print:
- one line per rollup field: `runs=..`, `all_healthy=yes|no`,
  `total_entries=..`, `max_estimated_tokens=..`, `identical_all=yes|no`
- then one line per log: `log <i>: entries=.. healthy=.. estimated_tokens=..`

Exit code: `0` iff `all_healthy` else `1`.

## Constraints
- Do NOT change the behavior of any existing flag
  (--replay/--verify/--inspect/--trace/--compact/--budget/--audit/--compare).
- The new flag is handled in its own `if args.summarize is not None:` block,
  placed alongside the other read-only flags.

## Acceptance
`python3 -m deepseek_deharness "goal" --summarize <a> <b>` prints the rollup and
per-log lines and exits 0 for a healthy pair / 1 if any log is unhealthy; all
existing flags still behave as before (regression-checked).
