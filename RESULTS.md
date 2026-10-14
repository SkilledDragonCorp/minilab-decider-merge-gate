# RESULTS

Local green gate (before push). CI URL filled after the first green Actions run on `main`.

| Check | Result | Duration | Notes |
| --- | --- | --- | --- |
| `HF_HUB_OFFLINE=1 uv run pytest -q` | **pass** | 4.79s | 12 passed, 1 deselected (live) |
| `uv run ruff check .` | **pass** | 0.38s | |
| `uv run ruff format --check .` | **pass** | | |
| `python3 scripts/check-skills` | **pass** | | skills-layout OK |
| `python3 scripts/check-banned-phrases` | **pass** | | banned-phrases OK |
| `python3 scripts/check-upstream-pin` | **pass** | | `8b6faa553038a59e73fa7f16c4081f8ceb21d27e` |
| `python3 scripts/check-upstream-parity` | **pass** | | upstream-parity OK |
| CI run URL | pending | | update after Actions |

Upstream SHA (`git -C upstream rev-parse HEAD`): `8b6faa553038a59e73fa7f16c4081f8ceb21d27e`
