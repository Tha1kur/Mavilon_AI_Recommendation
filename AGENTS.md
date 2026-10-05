# Repository guidance

Mavilon is in private development toward a later public launch. Foundation work is not release approval. Preserve application behavior during the current foundation phase; the defects in [ROADMAP.md](ROADMAP.md) require a separate remediation change.

- Frontend: Next.js App Router/React/TypeScript in `app/`, `components/`, `lib/`, and `types/`. Backend: FastAPI/SQLAlchemy in `backend/`.
- Use [README.md](README.md) for setup and canonical commands, [requirements](docs/requirements.md) for behavior/decisions, and [architecture](docs/architecture.md) for boundaries.
- Preserve `package-lock.json`, existing direct Python pins, environment examples, lint/compiler configuration, and historical documents. Do not modernize dependencies incidentally.
- Start the backend from `backend/`; configuration and SQLite paths depend on the working directory. Never point tests at a developer database or real credentials.
- Backend tests must use deterministic provider/model fixtures and temporary databases. Default checks must not download model weights or call TMDB. Live checks are separate and explicitly reported.
- Anonymous session IDs currently authorize access to behavioral data. Treat them, user databases, logs, real environment files, and provider keys as private. See [security](docs/security.md).
- Run checks appropriate to the change and record failures honestly. Do not suppress existing errors, weaken tests, or fix application behavior merely to make foundation checks green.
- Maintain the implementation sequence/status in [ROADMAP.md](ROADMAP.md), and verification evidence in [testing](docs/testing.md). Keep requirements, commands, and evidence in those canonical locations.
- Playwright, infrastructure provisioning, public deployment, and remote GitHub settings are outside this phase. Repository-side CI does not prove hosted protection is enabled.
