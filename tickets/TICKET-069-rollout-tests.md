# TICKET-069 — tests/test_rollout.py

## Capability
New test file `tests/test_rollout.py` proving `batch_rollout` composes the ledger view
into one consistent view with per-log final-response length detail, reports
health/identity/outcome/size/health-per-log/presence-per-log/tool-calls-per-log/
final-response-len-per-log correctly across a rollout, and never mutates any input log.

## Tests (5)
(a) **two byte-identical healthy logs**: runs=2, all_healthy=True, identical_all=True,
    total_entries = 2x one log's entries, max_estimated_tokens > 0, final_responses has
    length 2 with both entries equal and non-None, tool_calls_total = 2x one log's
    tool-call count, estimated_tokens_per_log has length 2 (both > 0),
    healthy_per_log == [True, True], has_final_response_per_log == [True, True],
    tool_calls_per_log == [n, n] where n is one log's tool-call count (> 0), and
    final_response_len_per_log == [L, L] where L is the character length of one log's
    final response (> 0).
(b) **pair where the second log is corrupted**: all_healthy=False and identical_all=False
    while final_responses still has length 2, estimated_tokens_per_log still has length 2,
    healthy_per_log == [True, False], has_final_response_per_log consistent with
    final_responses, tool_calls_per_log still has length 2, and final_response_len_per_log
    still has length 2 (the corrupt side's length is 0 iff its final response is None).
(c) **never mutates any input log**: all byte-identical before/after.
(d) **empty path list**: runs=0, all_healthy=True, total_entries=0, max_estimated_tokens=0,
    identical_all=True, final_responses=[], tool_calls_total=0, estimated_tokens_per_log=[],
    healthy_per_log=[], has_final_response_per_log=[], tool_calls_per_log=[],
    final_response_len_per_log=[].
(e) **single log with no assistant content**: final_response_len_per_log == [0].

## Constraints
- stdlib only; reuse the scripted transport + `run` helpers as in test_ledger.py.
