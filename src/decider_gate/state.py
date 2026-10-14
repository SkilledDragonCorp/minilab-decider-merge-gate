"""Build the strands-decider state string from a PR summary."""

from __future__ import annotations

import json

from .schema import PrSummary


def build_state(pr: PrSummary) -> str:
    paths = ", ".join(pr.touched_paths) if pr.touched_paths else "(none)"
    stats = pr.diff_stats
    lines = [
        f"title: {pr.title}",
        f"author: {pr.author or '(unknown)'}",
        f"base: {pr.base_ref or '(unknown)'} -> head: {pr.head_ref or '(unknown)'}",
        f"body: {pr.body or '(empty)'}",
        f"touched_paths: {paths}",
        (f"diff_stats: files={stats.files_changed} +{stats.additions} -{stats.deletions}"),
    ]
    if pr.ci_status is not None:
        lines.append(f"ci_status: state={pr.ci_status.state} conclusion={pr.ci_status.conclusion}")
    if pr.ocr_ripwire is not None:
        findings = "; ".join(pr.ocr_ripwire.findings) if pr.ocr_ripwire.findings else "(none)"
        lines.append(f"ocr_ripwire_risk: {pr.ocr_ripwire.risk or '(unset)'}")
        lines.append(f"ocr_ripwire_findings: {findings}")
    if pr.extra:
        lines.append(f"extra: {json.dumps(pr.extra, sort_keys=True)}")
    return "\n".join(lines)
