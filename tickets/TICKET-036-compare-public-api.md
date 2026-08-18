# TICKET-036 — export compare_logs from the package

## Capability
Additively export `compare_logs` from `deepseek_deharness/__init__.py` so it is
part of the public API, mirroring how `audit_log`, `diff_logs`, and the other
plain functions are exported.

## Rules
- Add `from .compare import compare_logs`.
- Add `"compare_logs"` to `__all__`, keeping the list sorted (ruff RUF022).
- Do NOT remove or reorder any existing export; additive only.
