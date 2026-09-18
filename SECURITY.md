# Security

## Reporting a vulnerability

This is a small personal/portfolio project (SIA Retention Engine), not a
maintained product with an SLA. If you find a security issue, please open
a private report via GitHub's "Report a vulnerability" feature on this
repo (Security tab) rather than a public issue, so it can be looked at
before details are public.

## Secrets and tokens

None of the following are ever committed to this repository:

- `GROQ_API_KEY` (the Decider agent's LLM provider)
- `HF_TOKEN` (Hugging Face write token, used only to *publish* the dataset
  and model from Colab -- never needed to *run* the app)

All of these are read from environment variables / a local `.env` file
(see `.env.example`), which is git-ignored. If a token is ever
accidentally exposed (for example, pasted into a notebook cell output),
it should be revoked and rotated immediately from the provider's
dashboard (Hugging Face: Settings -> Access Tokens; Groq: console.groq.com).

## Automated checks

Every push and pull request to `main` runs three independent gates
(`.github/workflows/ci.yml`):

- **Lint** (`ruff`) -- catches real bugs: undefined names, unused imports,
  broken syntax. Not a style-nitpick gate.
- **Security** (`bandit` + `pip-audit`) -- static-analyzes this repo's own
  code for common issues (hardcoded secrets, unsafe deserialization,
  shell injection, etc.) and scans the pinned dependencies in
  `requirements.txt` against known CVEs.
- **Tests** (`pytest`) -- the real test suite, including the model
  integration tests (fake classifier, no network or GPU needed).

## Model trust boundary

The trained churn model (`amaedaqureshi/sia-churn-model` on Hugging Face)
is downloaded at a **pinned revision** (`HF_MODEL_REVISION`, never
"latest") via `huggingface_hub.hf_hub_download` -- see
`backend/models/loader.py`. This means a new version of the model can't
silently change production behavior; upgrading requires an explicit
revision bump and redeploy.
