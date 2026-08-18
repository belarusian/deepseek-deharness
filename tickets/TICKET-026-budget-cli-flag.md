# TICKET-026 — CLI --budget LOG MAX_TOKENS flag

## Capability
`deepseek_deharness/__main__.py`: additive `--budget LOG MAX_TOKENS` flag that prints "fits=yes/no"
plus the planned compaction (max_messages + estimated tokens after) and exits 0. Do NOT change existing
flags' behavior (--replay, --verify, --inspect, --trace, --compact).

## Acceptance
- `python -m deepseek_deharness "goal" --budget <log> <n>` prints fits=yes/no + plan, exit 0.
- Existing flags unchanged (regression).
