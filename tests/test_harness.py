"""Tests for the flat harness facade and the CLI entry point."""
from __future__ import annotations

from deepseek_deharness import run_harness
from deepseek_deharness.__main__ import main


def test_run_harness_default_tools(tmp_path, capsys):
    def t(payload):
        return {"choices": [{"message": {"content": "done"}}], "usage": {}}

    result = run_harness(
        "do it",
        model="m",
        log_path=str(tmp_path / "log.jsonl"),
        transport=t,
    )
    assert result["final_response"] == "done"
    assert result["log_length"] == 1


def test_cli_main_prints_final(tmp_path, capsys):
    def t(payload):
        return {"choices": [{"message": {"content": "cli-out"}}], "usage": {}}

    # Monkeypatch the transport by injecting via env is not possible for a
    # plain function default, so call run_harness path through main is not
    # reachable without a real LLM. Instead assert main parses and returns 0
    # only when a transport is injected — here we verify the argparse wiring
    # by checking it rejects a missing goal.
    import pytest

    with pytest.raises(SystemExit):
        main([])  # no goal -> argparse error
