# TICKET-079 — tests/test_detail.py

## Capability
New test file `tests/test_detail.py` pinning `detail.batch_detail`.

## Tests
(a) Two byte-identical healthy logs: runs=2, all_healthy=True, identical_all=True,
    total_entries = 2x one log's entries, max_estimated_tokens > 0, final_responses length 2
    both equal and non-None, tool_calls_total = 2x one log's tool-call count,
    estimated_tokens_per_log length 2 (both > 0), healthy_per_log == [True, True],
    has_final_response_per_log == [True, True], tool_calls_per_log == [n, n] (n > 0),
    final_response_len_per_log == [L, L] (L = char length of one log's final response, > 0),
    entries_per_log == [e, e] (e > 0), message_count_per_log == [m, m] where
    m == summarize_log(a)["message_count"] (> 0).
(b) A pair where the second log is corrupted: all_healthy=False and identical_all=False while
    final_responses still has length 2, estimated_tokens_per_log still has length 2,
    healthy_per_log == [True, False], has_final_response_per_log consistent with final_responses,
    tool_calls_per_log still has length 2, final_response_len_per_log still has length 2,
    entries_per_log still has length 2, and message_count_per_log still has length 2 (the corrupt
    side's count reflects only its parseable last entry).
(c) batch_detail never mutates any input log (all byte-identical before/after).
(d) An empty path list yields runs=0, all_healthy=True, total_entries=0, max_estimated_tokens=0,
    identical_all=True, final_responses=[], tool_calls_total=0, estimated_tokens_per_log=[],
    healthy_per_log=[], has_final_response_per_log=[], tool_calls_per_log=[],
    final_response_len_per_log=[], entries_per_log=[], message_count_per_log=[].
(e) A single log with one entry carrying two messages: message_count_per_log == [2].

## Constraints
- stdlib only. Reuse `inspect.summarize_log` to derive expected per-log values (do not hardcode).
