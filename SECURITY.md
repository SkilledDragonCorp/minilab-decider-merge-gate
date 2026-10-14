# Security Policy

**Built by [SkilledDragon LLC](https://skilleddragon.com)**

This is a **SkilledDragon educational minilab**, not a production product. We do **not** maintain these repos on a regular schedule and we do **not** operate a vulnerability response program for them.

## Contact

General questions: **hello@skilleddragon.com**  
Do not use a dedicated security mailbox for this repo — none exists.

## If you find an issue

- Prefer reporting **upstream** when the issue is in [strands-labs/strands-decider](https://github.com/strands-labs/strands-decider).
- For something specific to this minilab's gate scripts or CI, you may email hello@skilleddragon.com. There is **no SLA**, and we may not patch or reply quickly.

## Supported versions

Only the commit currently on `main` is considered current for this educational lab.

## Secret handling

- Never commit `.env`, API keys, or tokens.
- Secrets are read from environment variables (local `.env`; GitHub Actions secrets in CI).
- CI required jobs set `HF_HUB_OFFLINE=1` and do not need Hub credentials.
- Optional `HF_TOKEN` is only for the live pytest slice when a checkpoint is gated (the default model card is not gated).
- Optional repository secret `CODECOV_TOKEN` is used only by the two verbatim Codecov upload steps in `upstream-ci` (`fail_ci_if_error: false`).
- Set `HF_HUB_DISABLE_TELEMETRY=1` and `DO_NOT_TRACK=1` for lab runs.

## Tooling pins

| Control | Pin |
| --- | --- |
| Upstream | `strands-labs/strands-decider` @ `8b6faa553038a59e73fa7f16c4081f8ceb21d27e` (Apache-2.0) |
| gitleaks | `v8.30.1` (pre-commit hook + CI binary with SHA256 verify) |
| Dependency audit | `uv export --frozen --format requirements-txt --no-emit-project --group gate > /tmp/req.txt`, drop VCS lines with `grep -v ' @ git+'`, then `uvx pip-audit --strict -r /tmp/req-pypi.txt` |

## Upstream license

`strands-labs/strands-decider` is Apache-2.0. Use at your own risk. Pin versions, review the code, and treat this as sample material.
