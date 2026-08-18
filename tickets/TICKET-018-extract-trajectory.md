# TICKET-018 — extract_trajectory: per-turn trajectory from an append-only log

## Capability
`deepseek_deharness/trace.py` (new module, stdlib only): `extract_trajectory(log_path) -> list[dict]`.
One record per parseable entry, in log order: `{turn: int, content: str|None, tool_calls: list[str|None], tool_results: list[dict]}`.
`tool_calls` = tool names from that entry's `step.tool_calls`; `tool_results` mirrors `step.tool_results`.
Must not mutate the log file; skip non-JSON entries (truncated tail).

## Acceptance
- Two-turn scripted run → 2 records with correct turn/content/tool_calls/tool_results.
- Never mutates the log (byte-identical before/after).
