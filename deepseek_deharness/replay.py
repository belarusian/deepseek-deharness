"""Replay & recovery — the append-only log as source of truth.

Cycle 1 recorded a decision: "the append-only log is the single source of
truth for reconciliation." This module makes that load-bearing. A run can be
*replayed* from its log alone (the outer spoke's journal) and a session can be
*recovered* from a log without re-calling the LLM.

Two plain functions, no plugin layer, no DI:

    reconstruct_session(log_path) -> Session
        Rebuild a Session from the LAST log entry's `messages`. The log is
        append-only, so the final entry holds the full conversation. An empty
        or missing log yields an empty Session().

    replay(log_path, *, transport=None, max_turns=8) -> dict
        Read the log, recover the session, and (only if a transport is given)
        re-run the remaining turns from that recovered state using the four
        algebra. With no transport this is a pure "re-read the log" path: it
        returns the reconstructed final response and message count and never
        touches an LLM.
"""
from __future__ import annotations

from pathlib import Path

from .llm_adapter import Transport
from .log import Log
from .run import inner_spoke, outer_spoke
from .session import Session


def reconstruct_session(log_path: str | Path) -> Session:
    """Rebuild a Session from the append-only log.

    The log is append-only and each entry records the full `messages` list at
    that point, so the LAST entry holds the complete conversation. We take it
    and rebuild a Session. An empty or missing log returns an empty Session().
    """
    path = Path(log_path)
    if not path.exists():
        return Session()
    entries = Log(path).read()
    if not entries:
        return Session()
    last = entries[-1]
    messages = last.get("messages", [])
    return Session(messages=list(messages))


def replay(
    log_path: str | Path,
    *,
    transport: Transport | None = None,
    max_turns: int = 8,
) -> dict:
    """Replay a run from its append-only log.

    Recovers the session from the log (see `reconstruct_session`). If no
    ``transport`` is given this is a pure re-read: it returns the recovered
    final response and message count without calling any LLM. If a transport
    IS given, it re-runs up to ``max_turns`` additional turns from the
    recovered state via the four algebra (inner/outer spoke), reconciling each
    new turn into the same log, until a final answer is produced.

    Returns a dict with keys:
      final_response : str | None  (last assistant content in the recovered run)
      messages       : list[dict]  (the recovered conversation)
      message_count  : int         (len of `messages`)
      log_length     : int         (reconciliation cursor after replay)
    """
    path = Path(log_path)
    session = reconstruct_session(path)

    # Pure re-read path: no transport -> never call an LLM.
    if transport is None:
        return {
            "final_response": _last_assistant_content(session.messages),
            "messages": list(session.messages),
            "message_count": len(session.messages),
            "log_length": len(Log(path)) if path.exists() else 0,
        }

    # Continuation path: re-run remaining turns from the recovered state.
    log = Log(path)
    final = _last_assistant_content(session.messages)
    for _ in range(max_turns):
        step = inner_spoke("", session, [], model="replay", transport=transport)
        outer_spoke(log, step, session=session)
        if not step.get("tool_calls"):
            final = step.get("content")
            break

    return {
        "final_response": final,
        "messages": list(session.messages),
        "message_count": len(session.messages),
        "log_length": len(log),
    }


def _last_assistant_content(messages: list[dict]) -> str | None:
    """Return the content of the last assistant message, or None if absent."""
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            return msg.get("content")
    return None
