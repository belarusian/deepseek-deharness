# TICKET-055 — CLI --batch LOG [LOG ...] flag

## Capability
Add an additive `--batch` flag to `deepseek_deharness/__main__.py`:

    --batch LOG [LOG ...]   (metavar="LOG", nargs="+", type=str, default=None)

When set, call `batch_report(args.batch)` and print:
- one line per rollup field:
  `runs=`, `all_healthy=yes|no`, `total_entries=`, `max_estimated_tokens=`,
  `identical_all=yes|no`, `tool_calls_total=`;
- one line per log:
  `log <i>: healthy=yes|no final_response=<value or -> estimated_tokens=..`
  (zip `healthy_per_log`, `final_responses`, `estimated_tokens_per_log`).

Exit `0` iff `all_healthy` else `1`.

## File paths / signatures
- `deepseek_deharness/__main__.py` — additive only: new import of
  `batch_report`, new `parser.add_argument("--batch", ...)`, and a new
  `if args.batch is not None:` handling block. Do NOT change the behavior of any
  existing flag (--replay/--verify/--inspect/--trace/--compact/--budget/
  --audit/--compare/--summarize/--aggregate/--rollup).

## Acceptance tests
- CLI end-to-end on two byte-identical healthy logs: prints all six rollup lines
  plus one `log <i>: healthy=yes final_response=... estimated_tokens=..` line per
  log; exit 0.
- On a pair with one corrupted log: `all_healthy=no`, the corrupt side prints
  `healthy=no`; exit 1.
- Existing flags still behave as before (regression).

## Inversion
A plain argparse flag calling one plain function — not a dsh CLI plugin/profile
command.
