# TICKET-045 — CLI --aggregate LOG [LOG ...] flag

## Capability
Add an additive `--aggregate` flag to `deepseek_deharness/__main__.py`:

    --aggregate LOG [LOG ...]   (nargs="+")

Behavior:
- Print one line per rollup field: runs / all_healthy=yes|no / total_entries /
  max_estimated_tokens / identical_all=yes|no / tool_calls_total.
- Then print one line per log's final response: `log <i>: final_response=<value or ->`
  (use `-` when the value is None).
- Exit 0 iff all_healthy else 1.

## Rules
- Additive only: do NOT change existing flags' behavior (--replay/--verify/
  --inspect/--trace/--compact/--budget/--audit/--compare/--summarize).
- Reuse `aggregate.aggregate_runs`. stdlib only (argparse). No new dependencies.
