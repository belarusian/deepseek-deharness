# TICKET-028 — audit_log: one read-only health report composing the per-concern functions

## Capability
`deepseek_deharness/audit.py` (new module, stdlib only): `audit_log(log_path) -> dict`.
A single read-only health report that composes the existing per-concern functions into one view.
Returns a dict with exactly these keys:
  - `entries`          : int — number of log lines (from `inspect.summarize_log`).
  - `healthy`          : bool — True iff `repair.verify_log(log_path) == []`.
  - `violations`       : list[dict] — the raw violation records from `repair.verify_log`.
  - `final_response`   : str | None — last assistant content (from `inspect.summarize_log`).
  - `tool_calls`       : int — count of tool calls seen across any entry's step
                         (`len(inspect.summarize_log(...)["tool_calls"])`).
  - `estimated_tokens` : int — from `compact.estimate_tokens`.

MUST reuse `repair.verify_log`, `inspect.summarize_log`, and `compact.estimate_tokens` (import them;
do not re-implement their logic). Stdlib only. Must not mutate the log file.

## Acceptance
- On a healthy two-turn log: entries>0, healthy=True, violations=[], final_response is not None,
  tool_calls>=1, estimated_tokens>0.
- On a corrupted log (truncated/invalid JSON tail line): healthy=False with at least one violation,
  while still returning the recoverable fields (entries, final_response, tool_calls, estimated_tokens).
- Never mutates the original log (byte-identical before/after).
- Empty/missing log → entries=0, healthy=True, violations=[], final_response=None, tool_calls=0,
  estimated_tokens=0.
