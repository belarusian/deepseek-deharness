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

from collections.abc import Callable
from typing import Any

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
    kwargs: dict[str, Any] = {"tools": schema or None}
    if transport is not None:
        kwargs["transport"] = transport
    resp = call_llm(session.messages, model, **kwargs)

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

    Example (stub transport, no real LLM)::

        from deepseek_deharness.run import run
        from deepseek_deharness.tools import builtin_tools

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

        result = run(
            "add 2 and 3",
            model="deepseek-v4-flash",
            system="You are a calculator.",
            tools=builtin_tools(),
            log_path="/tmp/log.jsonl",
            transport=stub,
        )
        # -> {"final_response": "the answer is 5",
        #     "messages": [...], "log_length": 2}

    Returns a dict with keys ``final_response`` (str | None), ``messages``
    (list[dict]) and ``log_length`` (int, the reconciliation cursor).
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
