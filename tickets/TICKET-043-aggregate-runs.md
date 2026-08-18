# TICKET-043 — aggregate_runs: read-only multi-run report with per-log detail

## Capability
New module `deepseek_deharness/aggregate.py` with one plain function:

    aggregate_runs(paths) -> dict

A read-only multi-run report that composes the existing batch rollup
(`summarize.summarize_runs`) with per-log detail (`inspect.summarize_log`) into
one view. Takes an iterable of log paths and returns:

    {
      "runs": int,                    # from summarize_runs
      "all_healthy": bool,            # from summarize_runs
      "total_entries": int,           # from summarize_runs
      "max_estimated_tokens": int,    # from summarize_runs
      "identical_all": bool,          # from summarize_runs
      "final_responses": list[str | None],  # [inspect.summarize_log(p)["final_response"] for p in paths]
      "tool_calls_total": int,        # sum over each log's inspect.summarize_log(p) of len(tool_calls)
    }

`final_responses` is aligned with the input order (one entry per log); a log
with no assistant content yields `None`.

## Implementation rules
- Reuse `summarize.summarize_runs(paths)` for the five rollup keys — do NOT
  re-derive them.
- Reuse `inspect.summarize_log(p)` for `final_responses` and `tool_calls_total`
  — do NOT re-implement their logic.
- stdlib only (json, pathlib). No new dependencies.
- Must not mutate any input log file.

## Acceptance tests
Covered by TICKET-044 (tests/test_aggregate.py).
