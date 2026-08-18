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

from .budget import fits_budget, plan_compaction
from .compact import compact_log
from .harness import run_harness
from .inspect import summarize_log
from .repair import verify_log
from .replay import replay
from .trace import extract_trajectory


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
    parser.add_argument(
        "--trace",
        metavar="LOG",
        default=None,
        help="Print one line per turn from an append-only log's trajectory and exit 0.",
    )
    parser.add_argument(
        "--compact",
        metavar="LOG",
        default=None,
        help="Write a compacted copy of an append-only log to a temp file and print its path.",
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=4,
        help="Max messages per entry when using --compact (default 4).",
    )
    parser.add_argument(
        "--budget",
        metavar="LOG",
        nargs=2,
        type=str,
        default=None,
        help="Check whether an append-only log fits a token budget and print the planned compaction.",
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

    if args.trace is not None:
        for record in extract_trajectory(args.trace):
            content = record["content"]
            tools = ",".join(str(n) for n in record["tool_calls"]) or "-"
            results = len(record["tool_results"])
            print(
                f"turn {record['turn']}: {content if content is not None else '-'} "
                f"tools=[{tools}] results={results}"
            )
        return 0

    if args.compact is not None:
        result = compact_log(args.compact, max_messages=args.max_messages)
        print(f"path={result['path']}")
        print(f"entries={result['entries']}")
        print(f"messages_before={result['messages_before']}")
        print(f"messages_after={result['messages_after']}")
        return 0

    if args.budget is not None:
        budget_log, budget_max_tokens = args.budget[0], int(args.budget[1])
        fits = fits_budget(budget_log, max_tokens=budget_max_tokens)
        plan = plan_compaction(budget_log, max_tokens=budget_max_tokens)
        print(f"fits={'yes' if fits else 'no'}")
        print(f"max_messages={plan['max_messages']}")
        print(f"estimated_tokens_after={plan['estimated_tokens_after']}")
        return 0

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
