# TICKET-003: run() docstring usage example

**Cycle:** 2
**Status:** DONE
**File:** deepseek_deharness/run.py

## What
Added a concrete usage example to the run() function docstring showing how
to call run(goal, model=..., system=..., tools=builtin_tools(), log_path=...,
transport=stub) with a two-turn stub transport (tool call then final answer),
and documented the return shape: {final_response, messages, log_length}.

No public API change; docstring only.
