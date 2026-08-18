# TICKET-038 — summarize_runs: read-only multi-run rollup

## Capability
New module `deepseek_deharness/summarize.py` with one plain function:

    summarize_runs(paths) -> dict

A read-only rollup that composes the existing per-log views into a single
multi-run report. Takes an iterable of log paths and returns:

    {
      "runs": int,                    # number of logs given
      "logs": list[dict],             # [audit.audit_log(p) for p in paths]
      "all_healthy": bool,            # True iff every report is healthy
      "total_entries": int,           # sum of each report's `entries`
      "max_estimated_tokens": int,    # max of each report's `estimated_tokens` (0 if no logs)
      "identical_all": bool,          # True iff every pair of logs is byte-identical
    }

## Implementation rules
- Reuse `audit.audit_log` for each log and `compare.compare_logs` pairwise for
  `identical_all`. Do NOT re-implement their logic.
- `identical_all` is True iff every pair (i < j) reports `identical=True`; it is
  trivially True for 0 or 1 log (no pairs to compare).
- stdlib only (json, pathlib). No new dependencies.
- Must not mutate any input log file.

## Acceptance tests
Covered by TICKET-039 (tests/test_summarize.py).
