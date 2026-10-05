# Development plan and improvement backlog

Private development toward a later public launch. The owner approved foundation preparation only; application behavior changes, deployment and hosted GitHub settings remain outside this phase. Preserve existing useful configuration and versions. This plan extends the 2026-09-29 backlog rather than replacing its unverified work with a completion claim.

## Foundation sequence

| Step | Scope | Status / completion evidence |
| --- | --- | --- |
| A | Reproduce current frontend and direct backend requirements before changing dependency strategy | Complete: original installs, frontend build and isolated backend/model startup reproduced; see [testing](docs/testing.md) |
| B | Establish concise local guidance, requirements, actual architecture, testing/security context; reconcile stale provider documentation | Complete: canonical documentation integrated |
| C | Declare tested runtimes and the smallest evidence-backed dependency strategy, accounting for platform-sensitive ML packages | Complete for Python 3.12/macOS arm64; other backend platforms deliberately unverified |
| D | Canonical checks and focused deterministic backend tests | Complete: canonical checks; 15 tests pass and 2 expose existing defects |
| E | Fast native hook, pinned Gitleaks, npm/pip audits and repository-side GitHub Actions | Hosted deterministic checks pass; audits and known defects report existing debt; see testing evidence |
| F | Run applicable checks, test safeguard failure modes, distinguish existing failures/security findings from foundation regressions | Complete with documented failures/blockers; see testing evidence |
| G | Review complete diff for behavior preservation, useful docs, private/generated files and unresolved blockers | Complete: source/config preservation, dependency graph, audit hashes, docs links and safeguards reviewed; awaiting separate remediation approval |

[README](README.md) owns commands; [testing](docs/testing.md) owns executed verification evidence. No daily automation or deployment is implied. Foundation readiness and release readiness are separate.

## Next remediation change: contracts and truthful state

Define identity/history requirements before their affected implementation. These source findings remain intentionally untouched in the foundation phase:

- **APP-01 — Session contract:** [client](lib/api/user.ts) sends an existing ID in JSON; [backend](backend/routers/users.py) expects a query parameter. Verify that returning sessions do not create orphan users and continue to resolve their data.
- **APP-02 — Taste contract:** [backend response](backend/routers/users.py) declares string lists, while [service persistence](backend/services/user_service.py) and [profile UI](app/profile/page.tsx) use score dictionaries. Verify a populated profile and explicit failure state.
- **Failed mutations:** [card favorites](components/ui/ContentCard.tsx) repeat the optimistic value on failure; [profile deletions](app/profile/page.tsx) lack rollback/visible failure. Test add/remove, refresh and rejected writes.
- **History semantics:** [interaction service](backend/services/user_service.py) writes `interactions`; [history routes](backend/routers/history.py) read `watch_history`. Decide what history means before wiring it. Verify deletion/recalculation and retries against that decision.
- **Incomplete anime taste:** the [user service](backend/services/user_service.py) anime lookup branch is unfinished. Define parity/support expectations and verify them.
- **Fallback and similarity:** [movies router](backend/routers/movies.py) calls absent `get_popular_movies`; [similar route](backend/routers/content.py) passes a dictionary into model-oriented scoring and masks errors as empty results. Exercise failure paths with deterministic provider fixtures.
- **Mutation/concurrency contracts:** [retry interceptor](lib/api/client.ts) can replay mutations; user creation and multi-step writes require idempotency/transaction review. Preserve ownership and uniqueness under retries and concurrency.

### Remove the temporary CI exception with APP-01 / APP-02

The owner approved a foundation-only CI exception for exactly the two existing regressions. `Known application defects` runs them on every workflow event independently of the blocking jobs, with execution-step `continue-on-error: true`, normal failure output and a summary of the original step outcome. Setup failures remain failures. This is not a release waiver. All deterministic foundation checks remain blocking; dependency audits have their separate DEP-01 exception below.

The next remediation PR must fix APP-01/APP-02 without weakening these tests, demonstrate both pass, switch the blocking backend job from `backend-foundation` back to `backend`, and remove the temporary job plus `KNOWN_APPLICATION_DEFECTS`/partition commands and their guard test. If fixes land separately, return each fixed test to blocking coverage in that same PR; do not leave a fixed test under the exception. Default local `backend`/`all` already include both tests. Document the removal and rerun the complete blocking suite. The exception cannot expand to additional tests without explicit approval.

Split this scope into reviewable changes if fixing all contracts together obscures behavior review. The session/profile regressions already fail in the foundation suite. Extend regression tests with each approved fix; do not change expectations solely to achieve green checks.

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
