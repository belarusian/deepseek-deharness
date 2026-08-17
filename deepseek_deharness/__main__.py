"""CLI — a flat argparse script, not a Cordis-hosted command.

deepseek-harness runs via a Cordis host + profile. The inversion is a plain
`python -m deepseek_deharness "goal"` that calls run_harness directly. A
`--replay LOG` flag instead replays a finished run from its append-only log
(the source of truth) without calling the LLM.
"""
from __future__ import annotations

import argparse
import os

from .harness import run_harness
from .replay import replay


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deepseek_deharness",
        description="Monolithic agent harness (the inversion of deepseek-harness).",
    )
    parser.add_argument("goal", help="The task for the agent.")
    parser.add_argument("--model", default=os.environ.get("DEH_MODEL", "deepseek-v4-flash"))
    parser.add_argument("--system", default=None, help="Optional system prompt.")
    parser.add_argument("--log", default=".deepseek-deharness/log.jsonl")
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument(
        "--replay",
        metavar="LOG",
        default=None,
        help="Replay a finished run from its append-only log instead of running fresh.",
    )
    args = parser.parse_args(argv)

    if args.replay is not None:
        result = replay(args.replay)
        print(result["final_response"] or "")
        return 0

    result = run_harness(
        args.goal,
        model=args.model,
        system=args.system,
        log_path=args.log,
        max_turns=args.max_turns,
    )
    print(result["final_response"] or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
