"""CLI exit-code contract."""

from __future__ import annotations

from pathlib import Path

from decider_gate.cli import run

FIX = Path(__file__).parent / "fixtures"


def test_cli_fake_allow_exit_0() -> None:
    code = run(["--pr-json", str(FIX / "safe-pr.json"), "--fake", "allow"])
    assert code == 0


def test_cli_fake_deny_exit_1() -> None:
    code = run(["--pr-json", str(FIX / "unsafe-pr.json"), "--fake", "deny"])
    assert code == 1


def test_cli_fake_escalate_exit_3() -> None:
    code = run(["--pr-json", str(FIX / "safe-pr.json"), "--fake", "escalate", "--threshold", "0.8"])
    assert code == 3


def test_cli_fake_load_fail_exit_2() -> None:
    code = run(["--pr-json", str(FIX / "safe-pr.json"), "--fake", "load-fail"])
    assert code == 2
