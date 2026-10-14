"""Decider protocol: yes/no (noul) + calibrated score confidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DeciderAnswers:
    """Mirrors strands-decider noul + score answers for one PR state."""

    noul: float
    score: float
    confidence: float
    model: str


class Decider(Protocol):
    def ask_merge_gate(self, state: str) -> DeciderAnswers:
        """Ask whether the PR is safe to auto-merge; raise on model load failure."""


class ModelLoadError(RuntimeError):
    """Raised when the underlying model cannot be loaded or evaluated."""
