# Verification strategy and evidence

## What the foundation proves

The foundation should make installation and checks repeatable and make existing failures visible. It does not prove public-launch readiness, live-provider availability, recommendation quality or complete user-journey correctness. Use [README.md](../README.md) for canonical commands and [ROADMAP.md](../ROADMAP.md) for remediation order.

The accepted operating stage is private development. Keep package versions and application behavior unchanged in this phase. When a baseline fails, retain the diagnostic and identify its owner/scope instead of suppressing it or adjusting behavior to obtain green results.

## Deterministic backend coverage

Tests live under `backend/tests/` and are selected independently from the legacy `backend/test_scoring.py`, an integration-style script requiring configured services. The latter is not a default unit test.

Focused tests should exercise real scoring and contract/persistence code with tiny deterministic content/embedding fixtures. They must not import the full application in a way that downloads model weights, call TMDB, use private environment files, or open the developer's SQLite database. Patch external/model boundaries explicitly; use temporary/in-memory database engines and dependency overrides where needed. A fake model is test isolation, not evidence that production model initialization works.

Prioritize ranking invariants, empty inputs, content-type filtering, limits, diversity, persistence uniqueness, session/profile contract compatibility, and provider failure semantics as their owning work is approved. Tests of currently known broken acceptance criteria should be linked to the remediation backlog; do not encode accidental defects as desired product behavior or hide unexpected failures with broad exception handling.

## Verification layers

| Layer | Purpose and limits |
| --- | --- |
| Static/configuration | Parse owned configuration/Python files, check whitespace and dependency-manifest consistency; no service startup |
| Frontend lint/type/build | Existing lint policy, TypeScript compilation and Next production build; report source failures separately from installation/tool compatibility failures |
| Backend deterministic | Focused pytest suite and package consistency; external effects isolated |
| Secrets/hooks | Redacted staged/repository scans; synthetic hook tests cover staged-versus-working-tree content, deletion, missing scanner, whitespace/private-file rejection and propagation of tool failures |
| Dependency audits | Separate network-dependent npm/pip audits; preserve exact affected package/version/advisory evidence; advisory-service errors are not passes |
| CI | Repeat local canonical commands on declared runners; hosted workflow execution and remote protection are separate evidence |
| Later live/manual | Controlled TMDB/model startup, actual discovery → details → favorite → refresh → profile, returning-session behavior, failed mutations, keyboard/mobile use and recovery |

Browser automation/Playwright is explicitly deferred until critical journeys and expected behavior stabilize. Later live checks require disposable data and deliberate model-cache handling; frontend build or `/health` alone cannot substitute for them.

Recommendation-quality evaluation is separate: agree representative movie/anime/mood/cold-start examples with the owner, inspect relevance/diversity/explanations, and record trade-offs. No numerical quality threshold or latency SLO has been approved.

## Evidence ledger

### Initial read-only audit (before foundation implementation)

- Git/source/configuration/documentation inspection; clean baseline commit `5aa3170` on `chore/engineering-bootstrap`.
- Python AST parse: 23 source files passed without importing application modules.
- JSON parse: four configuration/manifest files passed.
- Frontend root manifest and lockfile dependency declarations matched.
- `git diff --check` passed on the unchanged tree.
- No install, lint/type/build, app startup, model loading, API/browser journey, dependency audit, secret-history scan, restore test or hosted-setting verification was performed in that audit.

### Foundation implementation verification

Executed on **2026-10-05**, macOS **27.0.1 arm64**, Node **22.22.0**, npm **10.9.4**, Python **3.12.7**, starting from `5aa3170`. At that verification checkpoint the foundation changes were uncommitted. Canonical commands and setup prerequisites are in README.

| Check executed | Result / evidence |
| --- | --- |
| Original `npm ci` with unchanged dependency graph | PASS: 432 packages installed. Initial sandbox DNS failure was retried with network access. A dependency deprecation warning was retained. |
| Original backend direct-requirement install in a fresh venv | PASS: all 10 direct requirements installed at their existing pins; baseline `pip check` and imports of FastAPI/Pydantic/SQLAlchemy/NumPy/PyTorch/Transformers/Sentence Transformers passed. |
| `npm run lint`, `npm run typecheck`, `npm run build`; final canonical frontend check | PASS. Initial build could not fetch Google Fonts inside the sandbox; network-enabled retry and final check passed. Existing lint deprecation and stale Browserslist-data warnings remain. No ESLint policy changes. |
| Cold offline backend import with an empty isolated model cache | FAIL as expected from current startup design: required model assets unavailable; no developer DB/env used. This is recorded as an operational prerequisite, not suppressed by tests. |
| Actual Uvicorn startup with model downloads, loopback-only listener and disposable SQLite | PASS: `/health` returned 200 with `configuration.ai_model_ready=true`. No TMDB key was supplied; no content endpoint/provider journey was tested. Process terminated after the check. |
| Final platform constraints replay in a second fresh venv | PASS: binary-wheel install, `pip check`, exact `pip freeze` comparison and ML-library imports. All application dependencies retained their baseline versions. pip and the newly selected pytest tool were corrected to 26.2.1/9.0.3 for verified advisories. |
| `python3 scripts/check.py backend` with pytest 9.0.3 | **15 PASS, 2 FAIL**. `test_returning_session_matches_actual_frontend_request`: returned session differs from submitted session. `test_populated_profile_matches_persisted_and_frontend_shape`: HTTP 500 instead of 200. Both reproduce existing APP-01/APP-02; neither is skipped or expected-failure marked. 19 dependency/application deprecation warnings retained. |
| `python3 scripts/check.py gates` | PASS: 9 tests covering initial commits/spaces, staged-vs-unstaged whitespace, private-file addition/deletion/rename, committed private-file CI policy, missing/failing/wrong-version scanner, and real synthetic staged-secret detection with redacted output. |
| `python3 scripts/check.py static` | PASS: Python/JSON parse, source-tree private-path policy, manifest/lock root dependency/runtime consistency. It does not import the app. |
| Gitleaks 8.30.0 install and canonical `secrets` check | PASS: archive SHA256 checked against official release metadata; scans of the one-commit history and nonignored current source found no leaks. Ignored real local files and private recovery backups were not scanned. |
| Hook installation and direct empty-index invocation | PASS: executable POSIX hook, shell syntax check, clone-local `.githooks` activation, scanner prerequisites; prior hooksPath absent. Synthetic fixtures verify actual staged changes without staging this repository. |
| Workflow verification | PASS: YAML parsing and scoped invariants (40-character action SHAs, read-only token, bounded timeouts, no privileged PR event; initial workflow had no failure exception, superseded by the approved partition below). Action tag SHAs checked against upstream GitHub metadata. This is not a hosted workflow run or complete GitHub schema validation. |
| npm audit | **FAIL**: 25 affected package records — 1 critical, 18 high, 5 moderate, 1 low. No automatic fix. |
| Final pip-audit | **FAIL**: 28 finding records across 6 packages, 17 distinct primary advisory IDs. The advisory service returns duplicate records. The initial run had 42 records across 8 packages before tool-only corrections. |
| Source preservation / documentation review | PASS: original application files and direct Python requirements unchanged; npm resolution graph unchanged (only root engines metadata added). Historical docs and existing lint/compiler/image configuration preserved. Local Markdown targets and `git diff --check` verified. |

[Dependency snapshot](dependency-audit.json) records affected versions, advisory IDs and manifest hashes; [security triage](security.md#dependency-audit-triage) explains applicability limits. Transient diagnostic logs used `/private/tmp/mavilon-*` and are not guaranteed to survive session cleanup; this ledger and the audit snapshot are the durable record.

The socket guard is installed before test collection and rejects connection, DNS and datagram-send attempts. It is an in-process Python safeguard, not an OS sandbox for arbitrary subprocesses/native extensions. Tests import the actual users route with a patched external model constructor and an overridden in-memory database. The small test-only `/request` endpoint exercises the production request model through FastAPI, not the full recommendation route.

The full local gate remains nonzero because of the two application regressions. The approved CI partition below makes only their separate job non-blocking; advisory steps and all foundation jobs remain blocking. GitHub CI has **not run** and remote protections have **not been modified**. The backend job targets macOS 15 arm64 based on official runner documentation, but its hosted result and account availability remain unverified. Linux/Windows/CUDA backend behavior, live TMDB, browser journeys, accessibility, performance capacity, recommendation quality and backup restoration are not certified.

## Release evidence still required

After approved remediation: verify identity/privacy controls, returning-session and populated-profile contracts, truthful optimistic-write recovery, history semantics, fallback/similar behavior, bounded resource use and safe errors. Then establish the target environment, full startup/model provenance, provider failure behavior, backup/restore and migration rollback. Review hosted required checks separately once CI has run successfully. See [security.md](security.md) for the release conditions.


## Temporary CI regression partition

Owner-approved after the foundation checkpoint, 2026-10-05. The two tests are byte-for-byte unchanged and still execute. The blocking backend partition deselects only their exact node IDs because the separate `Known application defects` job runs both. It has no dependency on the other jobs, so their failures do not prevent it from starting. Job-level `continue-on-error: true` is the only exception; the pytest step returns its real exit code and displays complete failures. This follows [GitHub job-level failure handling](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idcontinue-on-error).

| Job ID / displayed check | Scope | Policy |
| --- | --- | --- |
| `frontend` | npm install, lint/type/build, npm audit | Blocking |
| `backend` | scoped Python install/consistency, `backend-foundation`, pip-audit | Blocking |
| `safeguards` | pinned scanner installation, static/private-path checks, gate tests, history/current-source secret scan | Blocking |
| `known-application-defects` / **Known application defects** | same backend environment, exact APP-01/APP-02 regressions | Temporarily non-blocking |

Node IDs:

- `backend/tests/test_users_contract.py::test_returning_session_matches_actual_frontend_request` — ROADMAP APP-01.
- `backend/tests/test_users_contract.py::test_populated_profile_matches_persisted_and_frontend_shape` — ROADMAP APP-02.

No test is skipped, marked xfail, deleted, weakened, or altered. `backend` and `all` retain their complete local scope. Removal is mandatory with the next APP-01/APP-02 remediation: restore blocking `backend`, remove the temporary job/partition/guard, and verify all tests pass. See [ROADMAP removal checklist](../ROADMAP.md#remove-the-temporary-ci-exception-with-app-01--app-02). Dependency advisories remain blocking and can still prevent a green workflow. This config does not modify hosted branch-protection settings.


Partition verification before the local foundation commit: `backend-foundation` passed **15 tests**, deselecting exactly the two regressions which `known-application-defects` executed and reported as **2 failures** (exit 1, full output). The regression file SHA256 was unchanged before/after the CI refinement. **10 safeguard tests passed**, including the exact partition/failure-propagation guard. Workflow YAML/policy validation verified four independent jobs, only the named job-level exception, and no step-level exception. Static checks and `git diff --check` passed. Hosted execution remains unverified.
