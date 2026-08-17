# TICKET-002: README documenting the four algebra

**Cycle:** 2
**Status:** DONE
**File:** README.md

## What
Expanded the one-line README into a full document (84 lines) covering:
- The four algebra (inner spoke / outer spoke / run loop) with prose.
- A runnable Quick-start example using run_harness with a stub transport
  (verified to run and print "the answer is 5", log_length 2).
- A Modules table mapping each module to its plain-function role.
- The dsh -> deepseek-deharness inversion check table.
- Test commands (pytest / ruff / mypy).

The quick-start example was executed on disk and confirmed accurate before
commit.
