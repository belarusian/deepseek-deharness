# TICKET-029 — tests/test_audit.py: prove audit_log composes correctly and never mutates

## Capability
`tests/test_audit.py` (new): tests for `deepseek_deharness.audit.audit_log`. Build a real two-turn
log with the scripted transport + `run(...)` pattern used in `tests/test_budget.py`, plus a corrupted
variant (append a truncated/invalid JSON tail line to a copy).

## Acceptance (each is a test)
- (a) healthy two-turn log → audit_log reports healthy=True, violations=[], final_response not None,
  tool_calls>=1, estimated_tokens>0.
- (b) corrupted log (invalid JSON tail) → healthy=False with at least one violation, while still
  returning the recoverable fields (entries, final_response, tool_calls, estimated_tokens).
- (c) audit_log never mutates the original log (byte-identical before/after).
- (d) empty and missing logs → entries=0, healthy=True, violations=[], final_response=None,
  tool_calls=0, estimated_tokens=0.
