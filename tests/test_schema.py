"""Schema tests for pr.json."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from decider_gate.schema import PrSummary

FIX = Path(__file__).parent / "fixtures"


def test_safe_pr_fixture_validates() -> None:
    raw = json.loads((FIX / "safe-pr.json").read_text(encoding="utf-8"))
    pr = PrSummary.model_validate(raw)
    assert pr.title.startswith("docs:")
    assert pr.touched_paths == ["README.md"]
    assert pr.diff_stats.files_changed == 1


def test_unsafe_pr_fixture_validates() -> None:
    raw = json.loads((FIX / "unsafe-pr.json").read_text(encoding="utf-8"))
    pr = PrSummary.model_validate(raw)
    assert ".github/workflows/ci.yml" in pr.touched_paths
    assert pr.ocr_ripwire is not None
    assert pr.ocr_ripwire.risk == "high"


def test_missing_title_rejected() -> None:
    with pytest.raises(ValidationError):
        PrSummary.model_validate({"touched_paths": ["a.py"]})
