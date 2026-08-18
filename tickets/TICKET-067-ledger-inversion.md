# TICKET-067 — inversion: batch_ledger is a plain function, not a plugin

## Capability
Guard the inversion invariant for the ledger capability. Where deepseek-harness
(dsh) would express a multi-run *ledger* as a plugin/profile bundle composed by
DI wiring (a per-log tool-call-count view assembled from a manifest plugin + an
inspect plugin), deepseek-deharness expresses it as ONE plain function that
reuses two existing plain functions.

## File paths / signatures
- `deepseek_deharness/ledger.py` — must contain exactly one public function
  (`batch_ledger`) and no class, no registry, no DI container, no composition
  object. It imports only `manifest.batch_manifest`, `inspect.summarize_log`,
  and stdlib (`pathlib`).

## Acceptance tests
- `git diff main` for this cycle is ADDITIVE ONLY: it adds `ledger.py`,
  `tests/test_ledger.py`, and additive edits to `__main__.py` / `__init__.py`;
  it changes NO existing public signature.
- `python3 -m mypy deepseek_deharness/` reports zero issues (the new module is
  fully typed).

## Inversion
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| ledger plugin / profile-composed per-log tool-call-count view | `ledger.batch_ledger()` (one function composing batch_manifest + summarize_log) |
| ledger composed by a bundle + DI wiring | `__main__.py --ledger LOG [LOG ...]` flag |
