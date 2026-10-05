# Architecture and environment boundaries

## Current system

This is a two-application MVP: a Next.js browser frontend calls a FastAPI backend through Axios; the backend fetches TMDB metadata and persists anonymous user behavior in SQLite. Keep these boundaries until a demonstrated requirement justifies change.

| Area | Source and responsibility |
| --- | --- |
| UI | `app/`, `components/`, `lib/context/`: home/discovery and profile views, local state, details and chat overlays |
| API client | `lib/api/`: endpoint wrappers, localStorage identity, 30-second request timeout and retry interceptor |
| HTTP backend | `backend/main.py`, `backend/routers/`: nine router groups, Pydantic contracts, CORS, request IDs, health and metrics |
| Content integration | `backend/services/tmdb_service.py`: TMDB movies and anime, normalization, provider timeouts and per-request concurrency limits |
| Recommendations | `backend/services/recommendation_service.py`: Sentence Transformers embeddings, NumPy scoring, mood/rating/popularity and diversity behavior |
| Personalization | `backend/services/user_service.py`: interactions and taste updates; separate embedding-model initialization |
| Chat/explanations | `backend/services/chat_service.py`, `explanation_service.py`, `taste_reasoning.py`: rule/keyword processing and generated explanation text, not an external LLM API |
| State | `backend/database.py`, `backend/models/user.py`: SQLAlchemy sessions, SQLite tables; `cache_service.py` and service-local caches are process memory |

Frontend versions are resolved by `package-lock.json`; direct backend versions are in `backend/requirements.txt`. Setup and selected runtime declarations are documented in [README.md](../README.md). This foundation does not replace Next.js, FastAPI, SQLite, or the embedding model.

## Data flow and ownership

1. The browser gets/stores `mavilon_session_id` in localStorage and sends it with user API calls. There is no separate authentication layer identified in the source.
2. Discovery/search/detail routes fetch and normalize TMDB results. Both movie and anime IDs refer to TMDB; historical AniList/OMDb comments do not describe active integrations.
3. Recommendation services combine content features, mood and stored taste. The default model name is `all-MiniLM-L6-v2`; package reproducibility does not pin downloaded model assets.
4. User interactions update SQLite and attempt taste recalculation. Favorites and watch history are separate tables. Interactions do not automatically establish watched history.
5. The profile combines user state with fetched metadata. Client retries can replay mutations; idempotency is not established.

| Table | Meaning and important constraint |
| --- | --- |
| `users` | Internal UUID, unique/indexed session identifier, created/last-active timestamps |
| `interactions` | User/content/type/event/mood and timestamp; no event deduplication constraint |
| `favorites` | User/content/type and timestamp; unique `(user_id, content_id)` |
| `watch_history` | Separate watched timestamp/completion record; normal frontend interaction flow does not write it |
| `taste_profiles` | One per user; JSON embedding, genre/mood values, count and update time |

Behavioral data and identity identifiers are private. SQLite is `sqlite:///./mavilon_users.db`, relative to process working directory. Start in `backend/`; tests must isolate their database. Startup calls `create_all` and ad hoc SQLite column migrations. Alembic is a dependency, but no versioned migration environment is established.

## Configuration and startup constraints

- `.env.local` supplies `NEXT_PUBLIC_API_URL`; it is browser-visible configuration, never a secret channel.
- `backend/.env` supplies TMDB credentials, embedding name, logging and server settings. Keep actual files untracked; examples contain no working credential.
- The Uvicorn CLI host/port in README control that invocation. `BACKEND_HOST`/`BACKEND_PORT` are used by the direct `main.py` entry point.
- `FRONTEND_URL` exists in settings but CORS origins are currently hardcoded to localhost ports 3000/3001 in `main.py`. Editing the environment value alone does not change allowed origins.
- `UserService` loads Sentence Transformers during module initialization; recommendation service also loads a model during startup. Importing the full app can perform heavyweight/model-network work before a health request is possible.
- `/health` includes model readiness/configuration but always reports `status: healthy`; it is not a release/readiness gate.
- Caches and metrics are per process. Multiple workers change memory usage/cache behavior and do not establish shared rate/resource controls.

## Reproducibility and delivery decisions

The original `npm ci` and direct `pip install -r backend/requirements.txt` both succeeded before dependency strategy selection. All existing application direct pins and the resolved npm package graph are preserved. The npm lockfile changes only to mirror root runtime metadata.

Retain **pip/venv with a platform-scoped constraints file**, not a new dependency manager. `backend/constraints/macos-arm64-py312.txt` records every installed application and development dependency version observed on Python 3.12.7/macOS arm64. A second clean environment installed the final constraints and reproduced the exact package versions, passed `pip check`, and imported the ML libraries. Only pip and the initially selected pytest tool were updated for verified advisories, to 26.2.1 and 9.0.3 respectively. No application dependency was updated. Constraints select versions; they are not an artifact-hash lock or a model-weight lock.

The observed ML closure includes sentence-transformers 2.3.1, torch 2.14.1, transformers 4.57.6, huggingface-hub 0.36.2, tokenizers 0.22.2, numpy 1.26.3 and scipy 1.16.3. Some wheels require macOS 14+. The repository-side backend CI targets the documented standard `macos-15` arm64 runner and checks its architecture explicitly; the first hosted install, dependency consistency check and foundation tests passed (see testing evidence). Frontend/safeguard jobs use Ubuntu 24.04. No GPU requirement is established. Do not apply this constraints file blindly to Linux, Windows, Intel macOS or CUDA: validate their wheel availability, platform-specific dependencies and runtime behavior first, then record separate constraints if they become supported targets.

Regenerate constraints only in a fresh, reviewed environment: install unchanged direct requirements, add reviewed development tools, capture `pip freeze` plus the pip version, compare every changed version, and replay in a second fresh environment. Do not freeze a global environment or silently resolve a new closure in CI. pip-tools, a universal lock, and extra environment tooling add no demonstrated value for the one currently verified backend platform. Package/model security remediation remains outstanding; repeatable installation is not an endorsement of vulnerable versions.

Evidence and scope: [testing.md](testing.md). Primary guidance: [pip repeatable installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/), [GitHub runner platforms](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

CI is repository-side verification, not deployment. No hosting target, production platform, GPU need, process count, migration policy, recovery objective, or operating owner is agreed. Before deployment: select the target; reproduce its dependency/model environment; establish backup and tested restore for SQLite; define a safe migration/rollback procedure; set configuration/secrets/logging boundaries; verify identity, error, correctness and resource controls. No production migration or provisioning is authorized by these notes.

There is no evidence yet requiring Redis, a vector database, containers, Kubernetes, or additional services. Known defects and deferred decisions are in [ROADMAP.md](../ROADMAP.md), [requirements.md](requirements.md), and [security.md](security.md).
