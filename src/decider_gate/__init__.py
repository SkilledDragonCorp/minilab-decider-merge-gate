"""Calibrated yes/no merge gate wrapping strands-decider."""

from __future__ import annotations

__version__ = "0.1.0"

DEFAULT_MODEL = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
DEFAULT_THRESHOLD = 0.8
SAFE_MERGE_QUESTION = "Is this agent PR safe to auto-merge?"
SAFE_SCORE_QUESTION = "How safe is this agent PR to auto-merge without a human?"
SAFE_SCORE_LEVELS = ("unsafe", "risky", "acceptable", "safe")
