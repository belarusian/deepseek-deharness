# TICKET-021 — CLI --trace LOG flag

## Capability
`deepseek_deharness/__main__.py`: additive `--trace LOG` flag that prints one line per turn
("turn N: <content or -> tools=[...] results=<n>") and exits 0. Do NOT change existing flags
(--replay, --verify, --inspect).

## Acceptance
- `python -m deepseek_deharness "goal" --trace <log>` prints one line per turn, exit 0.
- Existing flags unchanged (regression).
