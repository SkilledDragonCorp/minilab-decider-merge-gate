"""Unit tests with a deterministic fake decider."""

from __future__ import annotations

import json
from pathlib import Path

from decider_gate.fake import FakeDecider
from decider_gate.gate import decide, decide_or_fail_closed
from decider_gate.protocol import ModelLoadError
from decider_gate.schema import PrSummary

FIX = Path(__file__).parent / "fixtures"


def _pr(name: str) -> PrSummary:
    return PrSummary.model_validate(json.loads((FIX / name).read_text(encoding="utf-8")))


def test_allow_when_confident_yes() -> None:
    result = decide(
        _pr("safe-pr.json"),
        FakeDecider(noul=0.9, score=2.7, confidence=0.95),
        threshold=0.8,
    )
    assert result.decision == "allow"
    assert result.exit_code() == 0


def test_deny_when_confident_no() -> None:
    result = decide(
        _pr("unsafe-pr.json"),
        FakeDecider(noul=0.1, score=0.3, confidence=0.92),
        threshold=0.8,
    )
    assert result.decision == "deny"
    assert result.exit_code() == 1


def test_escalate_when_low_confidence() -> None:
    result = decide(
        _pr("safe-pr.json"),
        FakeDecider(noul=0.6, score=1.5, confidence=0.4),
        threshold=0.8,
    )
    assert result.decision == "escalate"
    assert result.exit_code() == 3


def test_model_load_failure_raises() -> None:
    try:
        decide(_pr("safe-pr.json"), FakeDecider(fail_load=True), threshold=0.8)
        raise AssertionError("expected ModelLoadError")
    except ModelLoadError:
        pass


def test_fail_closed_maps_load_error_to_deny() -> None:
    result = decide_or_fail_closed(
        _pr("safe-pr.json"),
        FakeDecider(fail_load=True),
        threshold=0.8,
    )
    assert result.decision == "deny"
    assert result.confidence == 0.0
    assert any("fail closed" in r for r in result.reasons)
