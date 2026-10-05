# Mavilon AI Recommendation

**Private development; not approved for public launch.** Mavilon is a Next.js/TypeScript frontend and FastAPI backend for movie/anime discovery, mood recommendations, chat, favorites and personalization. TMDB currently supplies both movies and anime; local Sentence Transformers embeddings support recommendation scoring. Chat uses rules/keywords and retrieval rather than an external LLM API.

The engineering foundation establishes repeatable checks and records existing defects. It does not certify end-to-end behavior, recommendation quality or production readiness. [Verification evidence](docs/testing.md) distinguishes executed checks from outstanding work, and [ROADMAP.md](ROADMAP.md) defines the next remediation scope.

## Setup

Use Node **22.22.0**, npm **10.9.4**, and Python **3.12.7**, declared in `.nvmrc`, `package.json`, and `.python-version`. The tested backend resolution is macOS Apple Silicon (arm64), using wheels requiring macOS 14 or newer; the actual local run was on macOS 27.0.1. Linux, Intel macOS, Windows and CUDA backend resolutions are not certified. Preserve the npm lockfile and existing direct Python requirements. See [dependency decisions](docs/architecture.md#reproducibility-and-delivery-decisions).

Frontend, from the repository root:

```sh
npm ci
cp .env.local.example .env.local
npm run dev
```

Backend, in a separate terminal, using Python 3.12:

```sh
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install pip==26.2.1
python -m pip install --only-binary=:all: -r requirements-dev.txt -c constraints/macos-arm64-py312.txt
cp .env.example .env
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Configure your own TMDB key in `backend/.env`. Keep actual environment files, databases and credentials local. Open http://localhost:3000. Do not overwrite an existing local environment file when repeating setup.

`NEXT_PUBLIC_API_URL` is browser-visible and defaults to `http://localhost:8000`. Start the backend from `backend/` because `.env` and SQLite use relative paths. The explicit Uvicorn CLI host/port control this invocation; backend host/port environment settings apply to the direct `main.py` entry point. `FRONTEND_URL` does not currently change CORS: origins are hardcoded to localhost ports 3000/3001.

Full app startup may download/load model weights during import and startup and requires more resources than deterministic checks. Model-cache availability and `/health` do not prove the complete application works. See [architecture](docs/architecture.md) for actual startup and data boundaries.

## Development checks

The foundation's canonical command entry point is `scripts/check.py`, run from the repository root using Python 3.12. Install backend development requirements and Gitleaks first. It uses `backend/.venv/bin/python` when present, otherwise the invoking interpreter; npm must be on PATH. Verification status is recorded in [testing](docs/testing.md). Do not confuse test fixtures with a successful live model/provider integration.

```sh
python3.12 scripts/check.py static
python3.12 scripts/check.py gates
python3.12 scripts/check.py backend
python3.12 scripts/check.py frontend
python3.12 scripts/check.py all
```

Security checks are separate because audits contact advisory services and require the corresponding environment/tool installation:

```sh
python3.12 scripts/check.py secrets
python3.12 scripts/check.py audit-npm
python3.12 scripts/check.py audit-python
```

Repository-native hook and Gitleaks setup:

```sh
python3.12 scripts/install-gitleaks.py
python3.12 scripts/install-hooks.py
```

The hook must remain fast: no dependency installation, network access or model loading during commits. CI runs checks independently; installing a hook does not configure GitHub protections. Existing frontend development commands remain `npm run dev`, `npm run lint`, `npm run build`, and `npm start` (after a successful build). The pre-commit hook checks staged whitespace, private/generated paths and secrets, including partially staged changes. CI additionally checks the full source-tree path policy and scans history. No pre-push hook is installed. Hook installation preserves existing configurations on conflict; undo this clone’s activation with `git config --local --unset core.hooksPath` (the previous setting was absent).

**CI structure:** `frontend` (clean install, lint/type/build), `backend` (scoped install/consistency and foundation tests), and `safeguards` are blocking. **Dependency advisories (npm)**, **Dependency advisories (python)**, and **Known application defects** run independently with temporary execution-step exceptions. Full audit/pytest output remains visible, and each job summary reports the real step outcome. Setup failures still fail jobs. See [CI policy and removal conditions](docs/testing.md#temporary-ci-regression-partition).

PRs validate through `pull_request`; only `main` pushes trigger push validation. Manual runs remain available. For the exact backend partitions, run `python3.12 scripts/check.py backend-foundation` and `python3.12 scripts/check.py known-application-defects`. Default local `backend` and `all` still run the complete suite and currently fail; audit commands also retain their real nonzero status. ROADMAP APP-01/APP-02 must restore full blocking regression coverage; DEP-01 owns dependency remediation and restoring blocking audits. Public release remains blocked by unresolved applicable high/critical dependency findings and the application release prerequisites. Hosted foundation execution is recorded in [testing](docs/testing.md); branch protections have not been configured. Do not bypass hooks as a normal workflow.

## Project context

The project is Medium in scope with a compact codebase, Normal provisional inherent product risk, and early-MVP maturity. Standard documentation coverage is consolidated into these canonical sources:

- [AGENTS.md](AGENTS.md): concise repository operating rules.
- [Requirements](docs/requirements.md): observed journeys, proposed acceptance and unresolved owner decisions.
- [Architecture](docs/architecture.md): actual stack, data flow, environment and delivery boundaries.
- [Testing](docs/testing.md): isolation strategy, verification evidence and limits.
- [Security](docs/security.md): sensitive boundaries, prioritized risks and release conditions.
- [ROADMAP.md](ROADMAP.md): implementation order and deferred defects.

Session handling, profile contracts, failed favorite/history writes, recommendation fallbacks and resource controls have known issues. Identity/history policy is not yet finalized. The foundation phase intentionally leaves these application behaviors unchanged; public release requires remediation and verification.

## Preserved cleanup history

The current local source, including unpublished UI/backend edits and removed obsolete services, was preserved during the 2026-09-29 storage cleanup. Dependencies and generated caches were removed then; runtime behavior, model accuracy and end-to-end operation were not revalidated in that cleanup. New verification results are recorded separately in [testing](docs/testing.md).

The previous local repository had one unpushed commit containing an oversized backend ZIP. That original history was preserved in a private recovery backup; this repository starts with a clean source snapshot. The existing GitHub repository was confirmed empty before publication. SQLite user databases and local environment files remain excluded from Git.

The [historical README](docs/README.pre-cleanup.md) refers to fallback services no longer present in current source. Its claims are historical, not fresh test evidence. `backend/test_scoring.py` is an integration-style script requiring configured services and is not the deterministic test suite. See [history](docs/HISTORY.md) for cleanup details.
