# TICKET-019 — trajectory_stats: aggregate stats over an append-only log

## Capability
`deepseek_deharness/trace.py`: `trajectory_stats(log_path) -> dict` returning
`{turns: int, total_tool_calls: int, tools_used: dict[str,int], final_response: str|None}`.
Must not mutate the log file.

## Acceptance
- Two-turn scripted run → turns=2, total_tool_calls=1, tools_used={"add":1}, final_response="the answer is 5".
- Multiple tool calls in one entry counted correctly.
