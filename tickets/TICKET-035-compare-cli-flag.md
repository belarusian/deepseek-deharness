# TICKET-035 — CLI --compare A B flag

## Capability
Add an additive `--compare A B` flag to `deepseek_deharness/__main__.py`. It
prints a one-line-per-field side-by-side health comparison of two append-only
logs and exits 0 iff BOTH logs are healthy, else 1.

## Behavior
Given `--compare A B`, call `compare.compare_logs(A, B)` and print:
- for log A: `a.entries`, `a.healthy` (yes/no), `a.violations` (count),
  `a.tool_calls`, `a.estimated_tokens`
- the same five fields for log B (`b.*`)
- `identical=yes|no`
- `divergent_at=<n>` or `divergent_at=-` when None

Exit code: `0` if both reports are healthy, else `1`.

## Rules
- Additive only: do NOT change the behavior of any existing flag
  (`--replay/--verify/--inspect/--trace/--compact/--budget/--audit`).
- Reuse `compare.compare_logs`; do not re-implement its logic.
- stdlib only (argparse). No new dependencies.
