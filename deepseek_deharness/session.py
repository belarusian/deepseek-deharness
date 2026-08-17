"""Session state — a plain dataclass, not a plugin.

In deepseek-harness the session log is a Cordis plugin. Here it is one
dataclass holding the conversation plus scratch context. No inheritance
hierarchy, no DI.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Session:
    """Holds the conversation and per-run scratch state."""

    messages: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def append(self, msg: dict) -> None:
        """Append one message (role/content/...) to the conversation."""
        self.messages.append(msg)

    def reset(self) -> None:
        """Clear the conversation but keep context/metadata."""
        self.messages = []

    def to_dict(self) -> dict:
        """Serialize to a plain dict (round-trips via from_dict)."""
        return {
            "messages": list(self.messages),
            "context": dict(self.context),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Rebuild a Session from a dict produced by to_dict()."""
        return cls(
            messages=list(data.get("messages", [])),
            context=dict(data.get("context", {})),
            metadata=dict(data.get("metadata", {})),
        )
