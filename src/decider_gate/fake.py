"""Deterministic fake decider for keyless unit tests."""

from __future__ import annotations

from .protocol import DeciderAnswers, ModelLoadError


class FakeDecider:
    """Implements the same ask_merge_gate interface as StrandsDeciderAdapter."""

    def __init__(
        self,
        *,
        noul: float = 0.9,
        score: float = 2.5,
        confidence: float = 0.95,
        model: str = "fake-decider",
        fail_load: bool = False,
    ) -> None:
        self.noul = noul
        self.score = score
        self.confidence = confidence
        self.model = model
        self.fail_load = fail_load
        self.calls: list[str] = []

    def ask_merge_gate(self, state: str) -> DeciderAnswers:
        self.calls.append(state)
        if self.fail_load:
            raise ModelLoadError("fake model load failure")
        return DeciderAnswers(
            noul=self.noul,
            score=self.score,
            confidence=self.confidence,
            model=self.model,
        )
