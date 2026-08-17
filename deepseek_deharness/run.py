"""The four algebra — the whole harness in one module.

run(G, V1, V2*)*
  - inner spoke: does the work and records its trajectory
  - outer spoke: reconciles an append-only log

This is the inversion of deepseek-harness, where the agent loop, tool
registry, session log and LLM adapter are 40+ Cordis plugins composed by
profiles/bundles/patches. Here they are plain functions in one flat program:

    inner_spoke(...)  -> does one turn of work, returns a trajectory step
    outer_spoke(...)  -> appends the step to the append-only log, reconciles

No plugin layer. No DI container. No meta-composition.
"""
from __future__ import annotations

from typing import Any, Callable

from .llm_adapter import call_llm
from .log import Log
from .session import Session
from .tools import dispatch, to_openai_tools

# A "goal" G is a plain string. V1 is the system prompt. V2* is the tool list.


def inner_spoke(
    goal: str,
    session: Session,
    tools: list[dict],
    *,
    model: str,
    transport: Callable | None = None,
) -> dict:
    """Inner spoke: do one turn of work and return its trajectory step.

    Appends the user goal (first turn only), calls the LLM, and if the model
    requested a tool, runs it and feeds the result back. Returns a dict
    describing what happened (the trajectory step).
    """
    if not session.messages:
        session.append({"role": "user", "content": goal})

    schema = to_openai_tools(tools)
    resp = call_llm(
        session.messages,
        model,
        transport=transport,
        tools=schema or None,
    )

    step: dict[str, Any] = {
        "content": resp.get("content"),
        "tool_calls": resp.get("tool_calls", []),
        "usage": resp.get("usage", {}),
    }

    # Assistant turn (with any tool_calls) goes into the session.
    assistant_msg: dict[str, Any] = {"role": "assistant", "content": resp.get("content")}
    if resp.get("tool_calls"):
        assistant_msg["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": {"name": tc["name"], "arguments": tc["arguments"]},
            }
            for tc in resp["tool_calls"]
        ]
    session.append(assistant_msg)

    # Execute any requested tools; each result becomes a tool message.
    for tc in resp.get("tool_calls", []):
        result = dispatch(tools, tc["name"], tc["arguments"])
        session.append(
            {"role": "tool", "tool_call_id": tc["id"], "content": str(result)}
        )
        step.setdefault("tool_results", []).append(
            {"name": tc["name"], "result": result}
        )

    return step


def outer_spoke(
    log: Log,
    step: dict,
    *,
    session: Session,
) -> int:
    """Outer spoke: append the trajectory step to the append-only log.

    Reconciliation = the log is the source of truth. Each step is appended
    exactly once; the log length is the reconciliation cursor.
    """
    entry = {
        "step": step,
        "messages": session.to_dict()["messages"],
    }
    return log.append(entry)


def run(
    goal: str,
    *,
    model: str,
    system: str | None = None,
    tools: list[dict] | None = None,
    log_path: str,
    max_turns: int = 8,
    transport: Callable | None = None,
) -> dict:
    """Run the agent to completion.

    The four algebra in action: loop the inner spoke (work + trajectory) and
    after each turn let the outer spoke reconcile the append-only log. Stops
    when the model returns a final answer (no tool calls) or max_turns is hit.
    """
    tools = tools if tools is not None else []
    session = Session()
    if system:
        session.append({"role": "system", "content": system})
    log = Log(log_path)

    final = None
    for _ in range(max_turns):
        step = inner_spoke(
            goal, session, tools, model=model, transport=transport
        )
        outer_spoke(log, step, session=session)
        if not step.get("tool_calls"):
            final = step.get("content")
            break

    return {
        "final_response": final,
        "messages": session.to_dict()["messages"],
        "log_length": len(log),
    }
