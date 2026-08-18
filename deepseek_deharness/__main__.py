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

from .aggregate import aggregate_runs
from .audit import audit_log
from .batch import batch_report
from .budget import fits_budget, plan_compaction
from .compact import compact_log
from .compare import compare_logs
from .harness import run_harness
from .inspect import summarize_log
from .ledger import batch_ledger
from .manifest import batch_manifest
from .repair import verify_log
from .replay import replay
from .rollout import batch_rollout
from .rollup import rollup_runs
from .summarize import summarize_runs
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
    parser.add_argument(
        "--audit",
        metavar="LOG",
        default=None,
        help="Print a one-line-per-field health report for an append-only log; exit 0 if healthy else 1.",
    )
    parser.add_argument(
        "--compare",
        metavar=("A", "B"),
        nargs=2,
        type=str,
        default=None,
        help="Print a side-by-side health comparison of two append-only logs; exit 0 iff both are healthy else 1.",
    )
    parser.add_argument(
        "--summarize",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run rollup over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--aggregate",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run report (rollup + per-log final responses) over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--rollup",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run rollup (aggregate + per-log size) over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--batch",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run batch report (rollup + per-log health) over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--manifest",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run manifest (batch + per-log final-response presence) over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--ledger",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run ledger (manifest + per-log tool-call count) over one or more append-only logs; exit 0 iff all are healthy else 1.",
    )
    parser.add_argument(
        "--rollout",
        metavar="LOG",
        nargs="+",
        type=str,
        default=None,
        help="Print a multi-run rollout (ledger + per-log final-response length) over one or more append-only logs; exit 0 iff all are healthy else 1.",
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

    if args.audit is not None:
        report = audit_log(args.audit)
        print(f"entries={report['entries']}")
        print(f"healthy={'yes' if report['healthy'] else 'no'}")
        print(f"violations={len(report['violations'])}")
        print(f"final_response={report['final_response']}")
        print(f"tool_calls={report['tool_calls']}")
        print(f"estimated_tokens={report['estimated_tokens']}")
        return 0 if report["healthy"] else 1

    if args.compare is not None:
        a_log, b_log = args.compare[0], args.compare[1]
        result = compare_logs(a_log, b_log)
        for prefix, rep in (("a", result["a"]), ("b", result["b"])):
            print(f"{prefix}.entries={rep['entries']}")
            print(f"{prefix}.healthy={'yes' if rep['healthy'] else 'no'}")
            print(f"{prefix}.violations={len(rep['violations'])}")
            print(f"{prefix}.tool_calls={rep['tool_calls']}")
            print(f"{prefix}.estimated_tokens={rep['estimated_tokens']}")
        print(f"identical={'yes' if result['identical'] else 'no'}")
        divergent = result["divergent_at"]
        print(f"divergent_at={divergent if divergent is not None else '-'}")
        return 0 if (result["a"]["healthy"] and result["b"]["healthy"]) else 1

    if args.summarize is not None:
        result = summarize_runs(args.summarize)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        for i, rep in enumerate(result["logs"]):
            print(
                f"log {i}: entries={rep['entries']} "
                f"healthy={'yes' if rep['healthy'] else 'no'} "
                f"estimated_tokens={rep['estimated_tokens']}"
            )
        return 0 if result["all_healthy"] else 1

    if args.aggregate is not None:
        result = aggregate_runs(args.aggregate)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, value in enumerate(result["final_responses"]):
            print(f"log {i}: final_response={value if value is not None else '-'}")
        return 0 if result["all_healthy"] else 1

    if args.rollup is not None:
        result = rollup_runs(args.rollup)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, (value, est) in enumerate(
            zip(result["final_responses"], result["estimated_tokens_per_log"])
        ):
            print(f"log {i}: final_response={value if value is not None else '-'} estimated_tokens={est}")
        return 0 if result["all_healthy"] else 1

    if args.batch is not None:
        result = batch_report(args.batch)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, (healthy, value, est) in enumerate(
            zip(
                result["healthy_per_log"],
                result["final_responses"],
                result["estimated_tokens_per_log"],
            )
        ):
            print(
                f"log {i}: healthy={'yes' if healthy else 'no'} "
                f"final_response={value if value is not None else '-'} estimated_tokens={est}"
            )
        return 0 if result["all_healthy"] else 1

    if args.manifest is not None:
        result = batch_manifest(args.manifest)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, (healthy, value, est, has_fr) in enumerate(
            zip(
                result["healthy_per_log"],
                result["final_responses"],
                result["estimated_tokens_per_log"],
                result["has_final_response_per_log"],
            )
        ):
            print(
                f"log {i}: healthy={'yes' if healthy else 'no'} "
                f"final_response={value if value is not None else '-'} estimated_tokens={est} "
                f"has_final_response={'yes' if has_fr else 'no'}"
            )
        return 0 if result["all_healthy"] else 1

    if args.ledger is not None:
        result = batch_ledger(args.ledger)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, (healthy, value, est, has_fr, n_tc) in enumerate(
            zip(
                result["healthy_per_log"],
                result["final_responses"],
                result["estimated_tokens_per_log"],
                result["has_final_response_per_log"],
                result["tool_calls_per_log"],
            )
        ):
            print(
                f"log {i}: healthy={'yes' if healthy else 'no'} "
                f"final_response={value if value is not None else '-'} estimated_tokens={est} "
                f"has_final_response={'yes' if has_fr else 'no'} tool_calls={n_tc}"
            )
        return 0 if result["all_healthy"] else 1

    if args.rollout is not None:
        result = batch_rollout(args.rollout)
        print(f"runs={result['runs']}")
        print(f"all_healthy={'yes' if result['all_healthy'] else 'no'}")
        print(f"total_entries={result['total_entries']}")
        print(f"max_estimated_tokens={result['max_estimated_tokens']}")
        print(f"identical_all={'yes' if result['identical_all'] else 'no'}")
        print(f"tool_calls_total={result['tool_calls_total']}")
        for i, (healthy, value, est, has_fr, n_tc, fr_len) in enumerate(
            zip(
                result["healthy_per_log"],
                result["final_responses"],
                result["estimated_tokens_per_log"],
                result["has_final_response_per_log"],
                result["tool_calls_per_log"],
                result["final_response_len_per_log"],
            )
        ):
            print(
                f"log {i}: healthy={'yes' if healthy else 'no'} "
                f"final_response={value if value is not None else '-'} estimated_tokens={est} "
                f"has_final_response={'yes' if has_fr else 'no'} tool_calls={n_tc} "
                f"final_response_len={fr_len}"
            )
        return 0 if result["all_healthy"] else 1

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
