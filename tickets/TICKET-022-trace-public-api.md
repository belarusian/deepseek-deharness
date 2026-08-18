# TICKET-022 — export extract_trajectory + trajectory_stats from the package

## Capability
`deepseek_deharness/__init__.py`: export `extract_trajectory` and `trajectory_stats` (additive).

## Acceptance
- `from deepseek_deharness import extract_trajectory, trajectory_stats` works.
- No existing public signature changed.
