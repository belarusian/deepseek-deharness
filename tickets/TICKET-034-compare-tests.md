# TICKET-034 — tests/test_compare.py for compare_logs

## Capability
A new test module `tests/test_compare.py` proving `compare.compare_logs` gives a
correct read-only side-by-side comparison, reports identical vs diverging
correctly, and never mutates either log.

## Required tests
1. **two byte-identical logs** → `identical=True`, `divergent_at=None`, and the
   two per-log audit reports are equal (`result["a"] == result["b"]`).
2. **two logs that differ at one entry** → `identical=False` with the correct
   `divergent_at` index, while both per-log audit fields are still populated
   (entries > 0, healthy is a bool, etc.).
3. **never mutates either log** → both files byte-identical before/after the call.
4. **empty vs non-empty pair** → `identical=False`, `divergent_at=0`, the empty
   side's report all-zero / healthy=True and the populated side's report filled in.

## Rules
- Use the same scripted-transport `_run_to_log` helper pattern as
  `tests/test_audit.py` / `tests/test_inspect.py`.
- stdlib only; no new dependencies.
