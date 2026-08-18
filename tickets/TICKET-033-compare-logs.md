# TICKET-033 — compare_logs: side-by-side health comparison of two logs

## Capability
A new plain function compare_logs(a_path, b_path) -> dict in a new module deepseek_deharness/compare.py.

It produces a read-only side-by-side health comparison of two append-only logs by
composing the existing per-concern functions — it adds no new logic, only a single
view over them.

## Signature
    def compare_logs(a_path: str | Path, b_path: str | Path) -> dict

## Return shape
    {
        "a":           <audit.audit_log(a_path)>,   # full audit report for log A
        "b":           <audit.audit_log(b_path)>,   # full audit report for log B
        "identical":   bool,                        # True iff byte-identical line-for-line
        "divergent_at": int | None,                 # first index where they differ (None if identical)
    }

## Rules
- `a` and `b` MUST be the full `audit.audit_log` reports for each log — reuse
  `audit.audit_log`, do NOT re-implement its logic.
- `identical` is True iff the two logs are byte-identical line-for-line. Reuse
  `inspect.diff_logs(a_path, b_path)`: identical iff `divergent_at is None` AND
  `a_entries == b_entries`.
- `divergent_at` is `inspect.diff_logs(a_path, b_path)["divergent_at"]`.
- stdlib only (pathlib). No new dependencies.
- MUST NOT mutate either log file (read-only).

## Acceptance tests (see TICKET-034)
- two byte-identical logs -> identical=True, divergent_at=None, a==b reports equal
- two logs differing at one entry -> identical=False with correct divergent_at
- never mutates either log (byte-identical before/after)
- empty vs non-empty pair -> identical=False, divergent_at=0
