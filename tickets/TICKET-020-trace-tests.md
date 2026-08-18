# TICKET-020 — tests/test_trace.py

## Capability
New test module covering extract_trajectory + trajectory_stats:
(a) two-turn run → correct per-turn records; (b) stats correct; (c) neither function mutates the log;
(d) truncated log returns leading turns only; (e) missing-file edge cases; (f) multiple tool calls counted.

## Acceptance
- All tests pass with `python3 -m pytest -q`.
