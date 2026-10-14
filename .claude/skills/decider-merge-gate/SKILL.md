---
name: decider-merge-gate
description: Build pr.json from gh pr view, run decider-gate, merge only on exit 0, request human approval on exit 3.
---

# decider-merge-gate

Calibrated System-1 merge gate for agent PRs using `strands-decider`.

## Steps

1. Build `pr.json` from the open PR and local gate outputs:

```bash
gh pr view --json title,body,author,baseRefName,headRefName,files,additions,deletions,statusCheckRollup > /tmp/gh-pr.json
python3 - <<'PY'
import json
from pathlib import Path
raw = json.loads(Path("/tmp/gh-pr.json").read_text())
files = [f.get("path") for f in raw.get("files") or []]
pr = {
  "title": raw["title"],
  "body": raw.get("body") or "",
  "author": (raw.get("author") or {}).get("login"),
  "base_ref": raw.get("baseRefName"),
  "head_ref": raw.get("headRefName"),
  "touched_paths": files,
  "diff_stats": {
    "files_changed": len(files),
    "additions": raw.get("additions") or 0,
    "deletions": raw.get("deletions") or 0,
  },
  "ci_status": {"state": "unknown", "conclusion": None},
}
Path("pr.json").write_text(json.dumps(pr, indent=2) + "\n")
print("wrote pr.json")
PY
```

2. Run the gate (threshold 0.8):

```bash
uv run decider-gate --pr-json pr.json --threshold 0.8
```

3. Interpret exit codes:

| Exit | Meaning | Action |
| --- | --- | --- |
| 0 | allow | Safe to merge (`gh pr merge`) |
| 1 | deny | Do not merge; fix the PR |
| 2 | model load failure | Fail closed; do not merge |
| 3 | escalate | Request human approval before merge |

4. Merge only on exit 0. On exit 3, stop and ask a human reviewer.
