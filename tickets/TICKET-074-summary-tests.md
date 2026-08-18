# TICKET-074 — tests/test_summary.py (batch_summary test suite)

## Capability
New test file `tests/test_summary.py` that pins the behavior of
`summary.batch_summary`.

## Tests
1. **two byte-identical healthy logs** — on two identical healthy logs, batch_summary
   reports runs=2, all_healthy=True, identical_all=True, total_entries = 2x one log's
   entries, max_estimated_tokens > 0, final_responses has length 2 with both entries
   equal and non-None, tool_calls_total = 2x one log's tool-call count,
   estimated_tokens_per_log has length 2 (both > 0), healthy_per_log == [True, True],
   has_final_response_per_log == [True, True], tool_calls_per_log == [n, n] where n is
   one log's tool-call count (> 0), final_response_len_per_log == [L, L] where L is the
   character length of one log's final response (> 0), and entries_per_log == [e, e]
   where e is one log's entry count (> 0).
2. **a pair where the second log is corrupted** — all_healthy=False and
   identical_all=False while final_responses still has length 2,
   estimated_tokens_per_log still has length 2, healthy_per_log == [True, False],
   has_final_response_per_log consistent with final_responses, tool_calls_per_log still
   has length 2, final_response_len_per_log still has length 2, and entries_per_log
   still has length 2 (the corrupt side's count reflects only its parseable entries).
3. **never mutates any input log** — all byte-identical before/after.
4. **empty path list** — runs=0, all_healthy=True, total_entries=0,
   max_estimated_tokens=0, identical_all=True, final_responses=[], tool_calls_total=0,
   estimated_tokens_per_log=[], healthy_per_log=[], has_final_response_per_log=[],
   tool_calls_per_log=[], final_response_len_per_log=[], entries_per_log=[].
5. **a single log with one entry** — entries_per_log == [1].

## Constraints
- stdlib only; reuse the scripted transport + `run` helper pattern from test_rollout.py.
- Must pass under `python3 -m pytest -q`.
