"""Live slice: real default model; not required for keyless CI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from decider_gate.gate import decide
from decider_gate.schema import PrSummary
from decider_gate.strands_adapter import StrandsDeciderAdapter

FIX = Path(__file__).parent / "fixtures"
DEFAULT_MODEL = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"


@pytest.mark.live
def test_unsafe_pr_is_not_allow() -> None:
    if os.environ.get("HF_HUB_OFFLINE") == "1" and not os.environ.get("RUN_LIVE_OFFLINE"):
        pytest.skip("HF_HUB_OFFLINE=1; live slice needs Hub access or a warm cache")
    pr = PrSummary.model_validate(json.loads((FIX / "unsafe-pr.json").read_text(encoding="utf-8")))
    model = os.environ.get("DECIDER_MODEL", DEFAULT_MODEL)
    device = os.environ.get("DECIDER_DEVICE", "cpu")
    result = decide(pr, StrandsDeciderAdapter(checkpoint=model, device=device), threshold=0.8)
    assert result.decision != "allow", result.reasons
