# TICKET-060 — CLI --manifest LOG [LOG ...] flag

## Capability
Add an additive `--manifest LOG [LOG ...]` flag (nargs="+") to
`deepseek_deharness/__main__.py`. When set, it prints one line per rollup field
(runs / all_healthy=yes|no / total_entries / max_estimated_tokens /
identical_all=yes|no / tool_calls_total) plus one line per log
(`log <i>: healthy=yes|no final_response=<value or -> estimated_tokens=..
has_final_response=yes|no`), and exits 0 if all_healthy else 1.

## File paths / signatures
- `deepseek_deharness/__main__.py` (modified, additive only)
  - new argparse flag `--manifest` (metavar="LOG", nargs="+", type=str, default=None).
  - import `batch_manifest` from `.manifest`.
  - a new `if args.manifest is not None:` branch placed alongside the other
    multi-run branches.

## Constraints / acceptance
- Do NOT change any existing flag's behavior (--replay/--verify/--inspect/
  --trace/--compact/--budget/--audit/--compare/--summarize/--aggregate/
  --rollup/--batch). Regression-checked by the existing CLI tests.
- Exit code: 0 iff all_healthy else 1.

## Inversion
A flat argparse flag, not a Cordis-hosted command or profile bundle.
