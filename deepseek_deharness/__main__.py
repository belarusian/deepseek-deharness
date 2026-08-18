"""CLI — a flat argparse script, not a Cordis-hosted command.

deepseek-harness runs via a Cordis host + profile. The inversion is a plain
`python -m deepseek_deharness "goal"` that calls run_harness directly. A
`--replay LOG` flag instead replays a finished run from its append-only log
(the source of truth) without calling the LLM, and a `--verify LOG` flag audits
the log's invariants (exit 0 if healthy, 1 if any violation is found).
"""
from __future__ import annotations

import argparse
import os

from .harness import run_harness
from .inspect import summarize_log
from .repair import verify_log
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
    parser.add_argument(
        "--verify",
        metavar="LOG",
        default=None,
        help="Verify the append-only log's invariants; exit 0 if healthy, 1 on violation.",
    )
    parser.add_argument(
        "--inspect",
        metavar="LOG",
        default=None,
        help="Print a human-readable summary of an append-only log and exit 0.",
    )
    args = parser.parse_args(argv)

    if args.verify is not None:
        violations = verify_log(args.verify)
        if not violations:
            print("OK")
            return 0
        for v in violations:
            print(f"[{v['index']}] {v['type']}: {v['detail']}")
        return 1

    if args.inspect is not None:
        summary = summarize_log(args.inspect)
        print(f"entries={summary['entries']}")
        print(f"message_count={summary['message_count']}")
        print(f"roles={summary['roles']}")
        for tc in summary["tool_calls"]:
            print(f"tool_call {tc['index']} {tc['name']}")
        print(f"final_response={summary['final_response']}")
        print(f"healthy={summary['healthy']}")
        return 0

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
