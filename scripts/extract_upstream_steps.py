#!/usr/bin/env python3
"""Generate scripts/upstream-test.sh from ci/upstream/tests.yml.

Local leg: cpu job python 3.10 row (torch==2.7.1 + pins) then lint job.
Codecov steps are skipped locally.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_YML = ROOT / "ci" / "upstream" / "tests.yml"
OUT = ROOT / "scripts" / "upstream-test.sh"

# Local matrix leg for the cpu job
MATRIX = {
    "python": "3.10",
    "torch": "torch==2.7.1",
    "pins": "transformers==5.15.0 peft==0.21.0 huggingface_hub==1.5.0",
}

JOB_ORDER = ("cpu", "lint")


def substitute(text: str) -> str:
    s = text
    s = s.replace("${{ matrix.python }}", MATRIX["python"])
    s = s.replace("${{ matrix.torch }}", MATRIX["torch"])
    s = s.replace("${{ matrix.pins }}", MATRIX["pins"])
    return s


def eval_if(cond: str | None) -> bool:
    if not cond:
        return True
    c = substitute(cond).strip()
    # Skip Codecov locally (always).
    if "codecov" in c.lower() or "Upload coverage" in c:
        return False
    if "matrix.python == '3.12'" in c:
        return MATRIX["python"] == "3.12"
    if "matrix.python == '3.10'" in c:
        return MATRIX["python"] == "3.10"
    return True


def parse_jobs(yml: str) -> dict[str, list[dict]]:
    """Minimal YAML walker for GHA-style jobs/steps with run/env/if/uses/name."""
    lines = yml.splitlines()
    jobs: dict[str, list[dict]] = {}
    in_jobs = False
    current_job: str | None = None
    in_steps = False
    steps: list[dict] = []
    current: dict | None = None
    run_lines: list[str] | None = None
    run_indent = 0
    env_mode = False
    env_indent = 0
    with_mode = False

    def flush_step() -> None:
        nonlocal current, run_lines
        if current is not None:
            if run_lines is not None:
                current["run"] = "\n".join(run_lines)
            steps.append(current)
        current = None
        run_lines = None

    def flush_job() -> None:
        nonlocal current_job, steps, in_steps
        flush_step()
        if current_job is not None:
            jobs[current_job] = steps
        current_job = None
        steps = []
        in_steps = False

    i = 0
    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if run_lines is not None:
            if stripped == "" or indent > run_indent:
                # content under `|` typically indented +2 from `run:`
                prefix = run_indent + 2
                run_lines.append(line[prefix:] if len(line) >= prefix else line.lstrip())
                i += 1
                continue
            if current is not None:
                current["run"] = "\n".join(run_lines)
            run_lines = None

        if env_mode:
            if indent > env_indent and re.match(r"^[A-Z0-9_]+:", stripped):
                key, _, val = stripped.partition(":")
                if current is not None:
                    current.setdefault("env", {})[key] = val.strip().strip("'\"")
                i += 1
                continue
            env_mode = False

        if with_mode:
            if indent > env_indent and stripped and not stripped.startswith("- "):
                i += 1
                continue
            with_mode = False

        if re.match(r"^jobs:\s*$", line):
            in_jobs = True
            i += 1
            continue
        if not in_jobs:
            i += 1
            continue

        if indent == 2 and re.match(r"^[a-z0-9_-]+:\s*$", stripped):
            flush_job()
            current_job = stripped[:-1]
            i += 1
            continue

        if current_job and indent == 4 and stripped == "steps:":
            in_steps = True
            i += 1
            continue

        if in_steps and indent == 6 and stripped.startswith("- "):
            flush_step()
            current = {}
            rest = stripped[2:]
            if rest.startswith("name:"):
                current["name"] = rest[len("name:") :].strip().strip("'\"")
            elif rest.startswith("uses:"):
                current["uses"] = rest[len("uses:") :].strip()
            elif rest.startswith("run:"):
                val = rest[len("run:") :].strip()
                if val in ("|", ">"):
                    run_lines = []
                    run_indent = indent
                elif val:
                    current["run"] = val
            elif rest.startswith("if:"):
                current["if"] = rest[len("if:") :].strip()
            i += 1
            continue

        if in_steps and current is not None and indent >= 8:
            if stripped.startswith("name:"):
                current["name"] = stripped[len("name:") :].strip().strip("'\"")
            elif stripped.startswith("uses:"):
                current["uses"] = stripped[len("uses:") :].strip()
            elif stripped.startswith("if:"):
                current["if"] = stripped[len("if:") :].strip()
            elif stripped.startswith("run:"):
                val = stripped[len("run:") :].strip()
                if val in ("|", ">"):
                    run_lines = []
                    run_indent = indent
                elif val:
                    current["run"] = val
            elif stripped.startswith("env:"):
                env_mode = True
                env_indent = indent
                current.setdefault("env", {})
            elif stripped.startswith("with:"):
                with_mode = True
                env_indent = indent
            elif stripped.startswith("working-directory:"):
                current["working-directory"] = stripped[len("working-directory:") :].strip()
            i += 1
            continue

        i += 1

    flush_job()
    return jobs


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def emit(jobs: dict[str, list[dict]]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "# GENERATED by scripts/extract_upstream_steps.py — do not edit by hand.",
        "# Local leg: cpu (py3.10 + torch==2.7.1 + pins) then lint. Codecov skipped.",
        "set -euo pipefail",
        'ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"',
        'cd "$ROOT"',
        'test "$(git -C upstream rev-parse HEAD)" = "8b6faa553038a59e73fa7f16c4081f8ceb21d27e"',
        'export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"',
        'export HF_HUB_DISABLE_TELEMETRY="${HF_HUB_DISABLE_TELEMETRY:-1}"',
        "",
    ]
    for job_name in JOB_ORDER:
        steps = jobs.get(job_name, [])
        lines.append(f"echo '== upstream job: {job_name} =='")
        for step in steps:
            name = step.get("name", step.get("uses", "run"))
            if "codecov" in name.lower() or "codecov" in str(step.get("uses", "")).lower():
                lines.append(f"echo 'skip Codecov locally: {name}'")
                continue
            if step.get("uses"):
                uses = step["uses"]
                lines.append(f"echo 'skip action locally: {uses}'")
                continue
            run = step.get("run")
            if not run:
                continue
            if not eval_if(step.get("if")):
                lines.append(f"echo 'skip step (if): {name}'")
                continue
            run = substitute(run)
            wd = step.get("working-directory", "upstream")
            env = step.get("env") or {}
            lines.append(f"echo '-> {name}'")
            lines.append("(")
            lines.append(f'  cd "{wd}"')
            for k, v in env.items():
                lines.append(f"  export {k}={shell_quote(substitute(v))}")
            for cmd_line in run.splitlines():
                if cmd_line.strip():
                    lines.append(f"  {cmd_line}")
            lines.append(")")
            lines.append("")
    lines.append("echo 'upstream-test.sh OK'")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not UPSTREAM_YML.is_file():
        print(f"missing {UPSTREAM_YML}", file=sys.stderr)
        return 1
    jobs = parse_jobs(UPSTREAM_YML.read_text(encoding="utf-8"))
    for required in JOB_ORDER:
        if required not in jobs:
            print(f"missing job {required!r} in {UPSTREAM_YML}", file=sys.stderr)
            return 1
    OUT.write_text(emit(jobs), encoding="utf-8")
    OUT.chmod(OUT.stat().st_mode | 0o111)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
