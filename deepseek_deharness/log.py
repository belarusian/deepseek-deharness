"""Append-only log — a plain file-backed list, not a plugin.

In deepseek-harness the session log is a Cordis plugin. Here it is a flat
append-only journal: entries are only ever appended, never mutated. The outer
spoke of the four algebra reconciles against this log.
"""
from __future__ import annotations

import json
from pathlib import Path


class Log:
    """A minimal append-only journal.

    Entries are dicts. `append` is the only write; `read` returns them in
    order. Backed by a JSON-lines file so the log survives across runs.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, entry: dict) -> int:
        """Append one entry; returns its index (0-based)."""
        idx = len(self.read())
        line = json.dumps(entry, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return idx

    def read(self) -> list[dict]:
        """Return all entries in append order."""
        entries = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def __len__(self) -> int:
        return len(self.read())
