# RESULTS

| Check | Result | Duration | Notes |
| --- | --- | --- | --- |
| `HF_HUB_OFFLINE=1 uv run pytest -q` | **pass** | 4.79s local | 12 passed, 1 deselected (live) |
| `uv run ruff check .` | **pass** | 0.38s local | |
| `uv run ruff format --check .` | **pass** | | |
| `python3 scripts/check-skills` | **pass** | | skills-layout OK |
| `python3 scripts/check-banned-phrases` | **pass** | | banned-phrases OK |
| `python3 scripts/check-upstream-pin` | **pass** | | `8b6faa553038a59e73fa7f16c4081f8ceb21d27e` |
| `python3 scripts/check-upstream-parity` | **pass** | | upstream-parity OK |
| Lab CI (`lint` `test` `skills-layout` `secrets` `audit` + optional `live`) | **pass** | | [run 38521552828](https://github.com/SkilledDragonCorp/minilab-decider-merge-gate/actions/runs/38521552828) |
| Upstream CI (`upstream-parity` `cpu` `mac` `lint`) | **pass** | | [run 38520905143](https://github.com/SkilledDragonCorp/minilab-decider-merge-gate/actions/runs/38520905143) |

Upstream SHA (`git -C upstream rev-parse HEAD`): `8b6faa553038a59e73fa7f16c4081f8ceb21d27e`

All upstream steps in the reproduced workflow completed successfully (cpu 3.10 + 3.12, mac py3.12, lint). Codecov uploads stay green when `CODECOV_TOKEN` is absent because upstream sets `fail_ci_if_error: false`.
