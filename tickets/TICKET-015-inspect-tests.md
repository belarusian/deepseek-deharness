# TICKET-015: tests/test_inspect.py — cover summarize_log + diff_logs

**Status:** OPEN (Cycle 5)

## What
`tests/test_inspect.py` with at least these scenarios:
- (a) summarize_log on a real scripted run → correct entries/message_count/roles/final_response, healthy=True.
- (b) summarize_log on a truncated log → healthy=False, still returns recoverable fields.
- (c) diff_logs of two identical logs → common_prefix == len, divergent_at is None.
- (d) diff_logs of two logs sharing a prefix then diverging → correct common_prefix and divergent_at.
- (e) summarize_log never mutates the log file (byte-identical before/after).

## Evidence
- `tests/test_inspect.py` — 5+ tests, all passing under `python3 -m pytest -q`.

## Impact (before)
inspect.py would ship untested.

## Suggestion / Resolution
Write the five scenarios; reuse a scripted two-turn run fixture like test_repair.py.
