# TICKET-048 — rollup_runs: read-only multi-run report with per-log size detail

## Capability
New module `deepseek_deharness/rollup.py` with one plain function:

    rollup_runs(paths) -> dict

A read-only multi-run report that composes the existing aggregate view
(`aggregate.aggregate_runs`) with per-log *size* detail (`audit.audit_log`) into
one view. Takes an iterable of log paths and returns:

    {
      "runs": int,                    # from aggregate_runs
      "all_healthy": bool,            # from aggregate_runs
      "total_entries": int,           # from aggregate_runs
      "max_estimated_tokens": int,    # from aggregate_runs
      "identical_all": bool,          # from aggregate_runs
      "final_responses": list[str | None],  # from aggregate_runs
      "tool_calls_total": int,        # from aggregate_runs
      "estimated_tokens_per_log": list[int],  # [audit.audit_log(p)["estimated_tokens"] for p in paths]
    }

`estimated_tokens_per_log` is aligned with the input order (one entry per log).

## Implementation rules
- Reuse `aggregate.aggregate_runs(paths)` for the seven keys — do NOT re-derive
  them.
- Reuse `audit.audit_log(p)` for `estimated_tokens_per_log` — do NOT re-implement
  its logic.
- stdlib only (json, pathlib). No new dependencies.
- Must not mutate any input log file.

## Acceptance tests
Covered by TICKET-049 (tests/test_rollup.py).
