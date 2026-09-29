# Mavilon AI Recommendation

**Status: work in progress.** A Next.js/TypeScript frontend and FastAPI backend for movie/anime discovery, recommendations, and chat.

## Setup

Frontend, from the repository root:

```sh
npm ci
cp .env.local.example .env.local
npm run dev
```

Backend, in a separate terminal:

```sh
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Configure your own TMDB credentials in `backend/.env`. Keep the real environment files local. Open the frontend at http://localhost:3000. Installation and startup have not been reproduced in this cleanup.

## Baseline and limitations

The current local source, including unpublished UI and backend edits and removed obsolete services, is preserved. The backend SQLite user database and local environment files are excluded from Git.

The previous local repository had one unpushed commit containing an oversized backend ZIP. That original history was preserved in a private recovery backup; this repository starts with a clean source snapshot. The existing GitHub repository was confirmed empty before publication.

The original README refers to fallback services no longer present in the current source. Treat the current implementation and backlog as authoritative. `backend/test_scoring.py` is an integration-style script requiring configured services; it was not run.

Source was preserved during the 2026-09-29 storage cleanup. Dependencies and generated caches were removed. Runtime behavior, model accuracy, and end-to-end operation were not revalidated. Any README.pre-cleanup.md is historical documentation; its claims are not fresh test results.

See [ROADMAP.md](ROADMAP.md) for the next improvements.
