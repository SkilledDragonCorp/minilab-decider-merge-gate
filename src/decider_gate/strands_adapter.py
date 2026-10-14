"""Adapter over strands-decider SystemOneEngine (public API at the pin)."""

from __future__ import annotations

from . import (
    DEFAULT_MODEL,
    SAFE_MERGE_QUESTION,
    SAFE_SCORE_LEVELS,
    SAFE_SCORE_QUESTION,
)
from .protocol import DeciderAnswers, ModelLoadError


class StrandsDeciderAdapter:
    """Loads strands-decider via load_engine and asks noul + score."""

    def __init__(
        self,
        *,
        checkpoint: str = DEFAULT_MODEL,
        device: str = "cpu",
        engine: object | None = None,
    ) -> None:
        self.checkpoint = checkpoint
        self.device = device
        self._engine = engine

    def _ensure_engine(self) -> object:
        if self._engine is not None:
            return self._engine
        try:
            from strands_decider.infer import load_engine
        except Exception as exc:  # noqa: BLE001 — fail closed on any import/load error
            raise ModelLoadError(f"failed to import strands-decider: {exc}") from exc
        try:
            self._engine = load_engine(self.checkpoint, device=self.device)
        except Exception as exc:  # noqa: BLE001
            raise ModelLoadError(f"failed to load checkpoint {self.checkpoint}: {exc}") from exc
        return self._engine

    def ask_merge_gate(self, state: str) -> DeciderAnswers:
        from strands_decider.schema import NoulQuestion, ScoreQuestion

        engine = self._ensure_engine()
        questions = {
            "safe_merge": NoulQuestion(instructions=SAFE_MERGE_QUESTION),
            "safe_score": ScoreQuestion(
                instructions=SAFE_SCORE_QUESTION,
                criteria=list(SAFE_SCORE_LEVELS),
            ),
        }
        try:
            response = engine.ask(state, questions)  # type: ignore[attr-defined]
        except ModelLoadError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ModelLoadError(f"decider evaluation failed: {exc}") from exc

        noul_answer = response.answers["safe_merge"]
        score_answer = response.answers["safe_score"]
        return DeciderAnswers(
            noul=float(noul_answer.noul),
            score=float(score_answer.score),
            confidence=float(score_answer.confidence),
            model=str(response.model),
        )
