# deepseek-deharness

Everything is a Function. The exact inverse of DeepSeek Harness: where dsh
makes everything a Cordis plugin composed via profiles/bundles/patches,
deharness is one monolithic agent harness - loop + tools + session +
llm-adapter as plain functions, organized by the four algebra.

No plugin layer. No DI container. No meta-composition. One flat program.

## How it works: the four algebra

`run(G, V1, V2*)*` - a goal `G`, a system prompt `V1`, and a tool list `V2*`,
iterated until the model returns a final answer or `max_turns` is hit.

- **inner spoke** (`run.inner_spoke`) - does one turn of work: appends the
  goal (first turn only), calls the LLM, and if the model requested a tool,
  runs it and feeds the result back into the session. Returns a trajectory
  step.
- **outer spoke** (`run.outer_spoke`) - reconciles by appending that step to
  an append-only JSONL log. The log is the single source of truth.
- **run loop** (`run.run`) - loops the inner spoke and, after each turn, lets
  the outer spoke reconcile. Stops on a final answer (no tool calls).

The only injectable seam is `transport` (a plain callable), so tests never
hit a real LLM. Everything else is a direct function call.

## Quick start

```python
from deepseek_deharness import run_harness, builtin_tools

def stub(payload):
    # Turn 1: ask for a tool; turn 2: final answer.
    if any(m.get("role") == "tool" for m in payload["messages"]):
        return {"choices": [{"message": {"content": "the answer is 5"}}]}
    return {"choices": [{"message": {
        "content": None,
        "tool_calls": [{"id": "c1", "type": "function",
                        "function": {"name": "add",
                                     "arguments": '{"a": 2, "b": 3}'}}],
    }}]}

result = run_harness(
    "add 2 and 3",
    system="You are a calculator.",
    tools=builtin_tools(),
    log_path="/tmp/log.jsonl",
    transport=stub,
)
print(result["final_response"])  # -> the answer is 5
```

`run_harness` returns `{"final_response": str | None, "messages": list[dict],
"log_length": int}`.

## Modules

| Module | What it is |
|---|---|
| `llm_adapter.py` | `call_llm(messages, model, *, transport=...) -> dict{content, tool_calls, usage}` - plain function; the only seam is a swappable `transport` callable. |
| `session.py` | `@dataclass Session` (`messages`, `context`, `metadata`; `append`, `reset`, `to_dict`, `from_dict`). Per-run scratch state. |
| `tools.py` | tools as plain functions in a flat dict; `make_tool`, `to_openai_tools`, `dispatch`, `builtin_tools` (echo, add). No registry plugin. |
| `log.py` | `Log`: append-only JSONL journal (`append`, `read`, `__len__`). The outer spoke source of truth. |
| `run.py` | the four algebra: `inner_spoke`, `outer_spoke`, `run`. |
| `harness.py` | `run_harness(...)` - the single flat entry point (the inversion of dsh plugin boot). |

## Inversion check (dsh -> deepseek-deharness)

| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| model adapter plugin | `llm_adapter.call_llm()` |
| tool registry plugin | `tools.py` flat dict + `dispatch()` |
| session log plugin | `session.Session` dataclass + `log.Log` |
| agent loop plugin | `run.inner_spoke` / `run.outer_spoke` / `run.run` |
| Cordis profile/bundle/patch composition | none - `harness.run_harness()` calls the four algebra directly |
| DI container / shared context | none - plain function arguments |

## Tests

```bash
python3 -m pytest -q      # unit + e2e (scripted transport) + HTTP integration (mocked urllib)
python3 -m ruff check .   # lint
python3 -m mypy deepseek_deharness/  # types
```
