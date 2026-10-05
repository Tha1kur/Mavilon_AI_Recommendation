# Development plan and improvement backlog

Private development toward a later public launch. Foundation is merged; the owner authorized APP-01/APP-02 as the first application-remediation phase. Other behavior changes, deployment and hosted GitHub settings remain outside this change. Preserve existing useful configuration and versions. This plan extends the 2026-09-29 backlog rather than replacing its unverified work with a completion claim.

## Foundation sequence

| Step | Scope | Status / completion evidence |
| --- | --- | --- |
| A | Reproduce current frontend and direct backend requirements before changing dependency strategy | Complete: original installs, frontend build and isolated backend/model startup reproduced; see [testing](docs/testing.md) |
| B | Establish concise local guidance, requirements, actual architecture, testing/security context; reconcile stale provider documentation | Complete: canonical documentation integrated |
| C | Declare tested runtimes and the smallest evidence-backed dependency strategy, accounting for platform-sensitive ML packages | Complete for Python 3.12/macOS arm64; other backend platforms deliberately unverified |
| D | Canonical checks and focused deterministic backend tests | Complete: canonical checks; 15 tests pass and 2 expose existing defects |
| E | Fast native hook, pinned Gitleaks, npm/pip audits and repository-side GitHub Actions | Hosted deterministic checks pass; audits and known defects report existing debt; see testing evidence |
| F | Run applicable checks, test safeguard failure modes, distinguish existing failures/security findings from foundation regressions | Complete with documented failures/blockers; see testing evidence |
| G | Review complete diff for behavior preservation, useful docs, private/generated files and unresolved blockers | Complete: source/config preservation, dependency graph, audit hashes, docs links and safeguards reviewed; APP-01/APP-02 subsequently authorized below |

[README](README.md) owns commands; [testing](docs/testing.md) owns executed verification evidence. No daily automation or deployment is implied. Foundation readiness and release readiness are separate.

## First remediation change: APP-01 / APP-02

The core contracts below are resolved. Broader identity/history decisions and the other listed defects remain deferred:

- **APP-01 — Resolved:** JSON-only session lookup returns persisted identity and reuses the existing user. Unknown/invalid IDs fail explicitly; frontend storage follows server confirmation and survives transient errors. Original regression preserved; see [contract decisions](docs/requirements.md#app-01--app-02-contract-decisions).
- **APP-02 — Resolved:** response and frontend share numeric score maps, preserving fractional genre/mood scores and valid empty profiles. Legacy lists use the existing service conversion convention. Failed loads remain errors with a retry message; original regression preserved.
- **Failed mutations:** [card favorites](components/ui/ContentCard.tsx) repeat the optimistic value on failure; [profile deletions](app/profile/page.tsx) lack rollback/visible failure. Test add/remove, refresh and rejected writes.
- **History semantics:** [interaction service](backend/services/user_service.py) writes `interactions`; [history routes](backend/routers/history.py) read `watch_history`. Decide what history means before wiring it. Verify deletion/recalculation and retries against that decision.
- **Incomplete anime taste:** the [user service](backend/services/user_service.py) anime lookup branch is unfinished. Define parity/support expectations and verify them.
- **Fallback and similarity:** [movies router](backend/routers/movies.py) calls absent `get_popular_movies`; [similar route](backend/routers/content.py) passes a dictionary into model-oriented scoring and masks errors as empty results. Exercise failure paths with deterministic provider fixtures.
- **Mutation/concurrency contracts:** [retry interceptor](lib/api/client.ts) can replay mutations; user creation and multi-step writes require idempotency/transaction review. Preserve ownership and uniqueness under retries and concurrency.

### Remediation execution status

| Step | Status |
| --- | --- |
| Reproduce unchanged APP-01/APP-02 regressions | Complete: both failed before edits |
| Trace and define canonical session/profile contracts | Complete: [requirements](docs/requirements.md#app-01--app-02-contract-decisions), no algorithm/schema redesign |
| Implement fixes and important contract coverage | Complete: original regressions pass unchanged; additional request/storage/serialization tests |
| Restore full blocking backend CI | Complete: `backend` runs every test; temporary known-defects job, partition commands/constant and guard removed |
| Independent read-only session security review and complete verification | Complete: no introduced security blocker; 37 backend tests, 12 frontend contract tests, lint/type/build, 9 safeguard tests and Gitleaks pass; see [testing](docs/testing.md) |
| Commit/push | Remediation checkpoint approved; commit/PR authorized, no merge. Hosted CI and scoped BrowserAct QA follow. |

The foundation-only APP-01/APP-02 CI exception is removed. Dependency-advisory exceptions below are unchanged. Other application defects must receive separate scoped remediation; they are not covered by the retired two-test exception.

## DEP-01 — Dependency remediation and removal of advisory exceptions

The owner approved temporary step-level exceptions for the dedicated **Dependency advisories (npm)** and **Dependency advisories (python)** jobs during private foundation development. Both execute the unchanged canonical audit commands, show all findings, and summarize the execution outcome. No automatic fix, ignored advisory, or blanket acceptance of risk is authorized. Audit service/tool failures are unknown results requiring investigation, not successful security evidence.

A separate dependency-remediation change must triage the [recorded findings](docs/security.md#dependency-audit-triage), establish applicability, make minimum compatible fixes with regression verification, and rerun both audits. Remove each audit step's `continue-on-error` and temporary-exception documentation when its debt is resolved; keep the dedicated checks blocking thereafter. This exception ends before public release: unresolved applicable high/critical findings block launch. Any proposed per-advisory exception requires explicit review with applicability evidence, owner and expiry; this CI exception grants none.

## Before public exposure

- Remediate and verify identity lifecycle, identifier leakage in logs/paths, raw exception disclosure and private-data policy. See [security findings SEC-01/02/05](docs/security.md).
- Bound API inputs, cache growth, user creation, provider work and model concurrency; address synchronous/duplicate model initialization. Verify overload and recovery with controlled inputs (SEC-03).
- Establish the target deployment, supported runtime/model assets, readiness semantics, safe CORS, operating owner, migration procedure, backup and tested restore (SEC-06).
- Resolve verified dependency vulnerabilities in a narrowly scoped security change, preserving unrelated versions; record reachability and verification instead of blanket updates.
- Verify the actual chat, details, profile/history and persistence journeys, provider/model degradation, accessibility and responsive behavior. Consider Playwright only once expected journeys are stable.
- Review remote GitHub protection/secret settings after repository CI succeeds, under separate authorization.

## Deliberately deferred

No framework modernization, Docker/Kubernetes, Redis/vector database, scanner suite, Husky/lint-staged, paid service, or permanent agent infrastructure. No new product feature follows automatically from research or historical documentation. Product/release decisions and acceptance proposals are tracked in [requirements](docs/requirements.md); historical cleanup records remain in [docs/HISTORY.md](docs/HISTORY.md) and [docs/README.pre-cleanup.md](docs/README.pre-cleanup.md).
