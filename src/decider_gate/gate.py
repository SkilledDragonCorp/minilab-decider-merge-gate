"""Map decider answers to allow / deny / escalate."""

from __future__ import annotations

from . import DEFAULT_THRESHOLD
from .protocol import Decider, ModelLoadError
from .schema import GateResult, PrSummary
from .state import build_state


def decide(
    pr: PrSummary,
    decider: Decider,
    *,
    threshold: float = DEFAULT_THRESHOLD,
) -> GateResult:
    """Run the merge gate. Fail closed on ModelLoadError (caller maps to exit 2)."""
    state = build_state(pr)
    answers = decider.ask_merge_gate(state)
    reasons: list[str] = [
        f"noul={answers.noul:.4f} (yes leans toward allow)",
        f"score={answers.score:.4f} confidence={answers.confidence:.4f}",
        f"threshold={threshold:.4f}",
    ]

    if answers.confidence < threshold:
        reasons.append("confidence below threshold; escalate to human")
        return GateResult(
            decision="escalate",
            confidence=answers.confidence,
            reasons=reasons,
            noul=answers.noul,
            score=answers.score,
            model=answers.model,
        )

    if answers.noul >= 0.5:
        reasons.append("noul >= 0.5 and confidence meets threshold; allow")
        return GateResult(
            decision="allow",
            confidence=answers.confidence,
            reasons=reasons,
            noul=answers.noul,
            score=answers.score,
            model=answers.model,
        )

    reasons.append("noul < 0.5 with adequate confidence; deny")
    return GateResult(
        decision="deny",
        confidence=answers.confidence,
        reasons=reasons,
        noul=answers.noul,
        score=answers.score,
        model=answers.model,
    )


def decide_or_fail_closed(
    pr: PrSummary,
    decider: Decider,
    *,
    threshold: float = DEFAULT_THRESHOLD,
) -> GateResult:
    """Like decide, but converts ModelLoadError into a deny result with confidence 0."""
    try:
        return decide(pr, decider, threshold=threshold)
    except ModelLoadError as exc:
        return GateResult(
            decision="deny",
            confidence=0.0,
            reasons=[f"model load failure (fail closed): {exc}"],
            noul=None,
            score=None,
            model=None,
        )
