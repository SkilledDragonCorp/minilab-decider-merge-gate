"""CLI: decider-gate --pr-json pr.json --threshold 0.8"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from . import DEFAULT_MODEL, DEFAULT_THRESHOLD
from .fake import FakeDecider
from .gate import decide
from .protocol import ModelLoadError
from .schema import GateResult, PrSummary
from .strands_adapter import StrandsDeciderAdapter


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decider-gate",
        description=(
            "Calibrated yes/no merge gate using strands-decider. "
            "Exit 0=allow, 1=deny, 2=model-load-failure, 3=escalate."
        ),
    )
    parser.add_argument(
        "--pr-json",
        required=True,
        type=Path,
        help="Path to pr.json (title, diff stats, touched paths, CI status).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Escalate when confidence is below this value (default {DEFAULT_THRESHOLD}).",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("DECIDER_MODEL", DEFAULT_MODEL),
        help="Hugging Face checkpoint id for strands-decider.",
    )
    parser.add_argument(
        "--device",
        default=os.environ.get("DECIDER_DEVICE", "cpu"),
        help="Torch/MLX device passed to strands-decider load_engine (default cpu).",
    )
    parser.add_argument(
        "--fake",
        choices=("allow", "deny", "escalate", "load-fail"),
        default=None,
        help="Use a deterministic fake decider (for tests and dry runs).",
    )
    return parser


def _fake_from_choice(choice: str) -> FakeDecider:
    if choice == "allow":
        return FakeDecider(noul=0.92, score=2.8, confidence=0.95)
    if choice == "deny":
        return FakeDecider(noul=0.12, score=0.4, confidence=0.91)
    if choice == "escalate":
        return FakeDecider(noul=0.55, score=1.5, confidence=0.42)
    return FakeDecider(fail_load=True)


def run(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    raw = json.loads(args.pr_json.read_text(encoding="utf-8"))
    pr = PrSummary.model_validate(raw)

    if args.fake is not None:
        decider = _fake_from_choice(args.fake)
    else:
        decider = StrandsDeciderAdapter(checkpoint=args.model, device=args.device)

    try:
        result = decide(pr, decider, threshold=args.threshold)
    except ModelLoadError as exc:
        fail = GateResult(
            decision="deny",
            confidence=0.0,
            reasons=[f"model load failure (fail closed): {exc}"],
        )
        print(fail.model_dump_json(indent=2))
        return 2

    print(result.model_dump_json(indent=2))
    return result.exit_code()


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
