# TICKET-062 — inversion: batch_manifest is a plain function, not a plugin

## Capability
Guarantee the Cycle 18 change preserves the deepseek-deharness inversion: where
deepseek-harness (dsh) would express a multi-run manifest as a composed
plugin/profile bundle with DI wiring, deepseek-deharness expresses it as ONE
plain function (`manifest.batch_manifest`) plus one flat argparse flag.

## File paths / signatures
- `deepseek_deharness/manifest.py` — one module-level function, no classes, no
  plugin base, no composition object, stdlib only.
- `deepseek_deharness/__main__.py` — a flat argparse branch, not a Cordis host.

## Acceptance / invariants
- `git diff main` is ADDITIVE ONLY: no existing public signature changed; the
  only modified files are `__main__.py` and `__init__.py`, both purely additive.
- No new dependencies (stdlib only).
- The manifest family now forms a clean five-rung composition ladder: summarize
  (rollup) → aggregate (+outcome) → rollup (+size) → batch (+health) → manifest
  (+presence); each layer reuses the one below it and adds exactly one new
  per-log dimension.

## Inversion
| dsh (plugin) | deepseek-deharness (plain function) |
|---|---|
| multi-run manifest plugin / profile-composed report with per-log presence detail | `manifest.batch_manifest()` (one function composing batch_report) |
| manifest composed by a bundle + DI wiring | `__main__.py --manifest LOG [LOG ...]` flag |
