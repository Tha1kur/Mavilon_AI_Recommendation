# Security boundaries and release conditions

## Classification and scope

Inherent product risk is **Normal, provisional**: consumer content discovery with behavioral data and a server-side provider credential; no payment or regulated/high-consequence workflow was identified. The owner confirmed private development toward later public launch. **Current release readiness is insufficient** regardless of that risk label. Identity/privacy, correctness, and resource-control defects must be remediated and verified before public launch.

This is a source-grounded foundation assessment, not a penetration test or legal/compliance determination. No credential compromise or unauthorized access has been demonstrated. Local/CI scanners complement application review; passing scanners cannot establish authorization or privacy correctness.

## Assets and trust boundaries

- TMDB key: server-only credential used by the provider client; never put it in `NEXT_PUBLIC_*` or fixtures.
- Session identifiers: bearer-like access to a user's profile, interactions, favorites, and history. Their unpredictability does not replace lifecycle/access controls.
- Behavioral data, embeddings, SQLite files, logs and backups: private developer/user information.
- Browser → API: inputs and identity are untrusted. CORS is not authentication.
- API → TMDB/model distribution: external availability, content, package/model provenance and resource consumption require explicit handling.
- Developer/CI → dependencies: installs and audits contact external services; CI must not require application secrets or a real user database.

## Prioritized source findings, intentionally unremediated

| ID | Priority / evidence | Consequence and remediation verification |
| --- | --- | --- |
| SEC-01 | Before public exposure: [user lookup](../backend/services/user_service.py), [client identity](../lib/api/user.ts), [request logging](../backend/main.py) | Supplied IDs select/create users; identifiers are stored in localStorage, embedded in URL paths and logged. No expiry/revocation lifecycle is established. Decide identity policy; verify isolation, unknown/expired identity, replay, safe logging and recovery. UUID guessing is not the demonstrated issue. |
| SEC-02 | Before public exposure: route handlers, including [content](../backend/routers/content.py), [users](../backend/routers/users.py), [history](../backend/routers/history.py), and [TMDB client](../backend/services/tmdb_service.py) | Raw exceptions can reach responses/logs; provider credentials are query parameters. Synthetic provider failures must demonstrate that responses and captured logs do not expose credentials, session IDs or internals. Actual secret disclosure is not established by this source review. |
| SEC-03 | Before public exposure: [recommendations](../backend/services/recommendation_service.py), [user service](../backend/services/user_service.py), [cache](../backend/services/cache_service.py), route input declarations | Unbounded inputs/caches, request-driven user creation and synchronous/duplicate model work can exhaust CPU, memory, storage or provider quota. Establish limits and test rejection, concurrency, timeout and recovery using controlled fixtures; do not load-test an external provider. |
| SEC-04 | Before public exposure: [retry interceptor](../lib/api/client.ts), [user mutations](../backend/routers/users.py), [database](../backend/database.py) | Retried writes and concurrent creation can cause duplicate work/inconsistent responses. Verify idempotency, uniqueness handling and atomicity in a separate remediation change. |
| SEC-05 | Release prerequisite: [data model](../backend/models/user.py), startup migrations in [database](../backend/database.py) | Retention/deletion, backup/restore, operational access, migration ownership and recovery targets are undefined. Agree policy, implement it and verify restore/deletion before holding public-user data. |
| SEC-06 | Deployment prerequisite: [CORS and health](../backend/main.py), [configuration](../backend/config.py) | Hardcoded localhost CORS and optimistic health status are not production configuration/readiness controls. Choose hosting and enforce/test the intended origins and readiness behavior in the release/remediation phase. |

Application correctness findings are tracked alongside these risks in [ROADMAP.md](../ROADMAP.md). The foundation tests exposed APP-01/APP-02; their scoped remediation is recorded below. Broader security findings remain open.

## Foundation safeguards and operating rules

Use the pinned Gitleaks tool and canonical secret/audit commands in [README.md](../README.md). Scan staged content before commits and tracked/history content in CI as configured. Keep output redacted. Never allowlist a genuine credential simply to pass a check; if one is exposed, stop dissemination and coordinate revocation/rotation with its owner before any authorized history repair.

Dependency audits use npm audit and pip-audit with the preserved dependency versions. Audit results are time-sensitive, can require network access, and are recorded separately from deterministic checks in [testing.md](testing.md). Assess affected versions/reachability and fix verified issues in a reviewable dependency change; do not use blanket automatic fixes or silent suppression. A failed advisory lookup is an unknown result, not a clean audit.

The repository-native hook is a fast local aid, not a security boundary: it must inspect staged content, fail clearly when required tooling is unavailable, and perform no install/network calls. CI independently runs reviewed checks. CI must use minimal permissions, immutable action references, finite job timeouts, no production credentials, and no privileged pull-request execution.

Hosted branch rules, required checks, secret protection availability and permissions have **not** been configured or verified. Review them only after repository CI succeeds, under separate authorization. No external scanning service or paid tool is required for this phase.


## Dependency audit triage

Snapshot: [dependency-audit.json](dependency-audit.json), 2026-10-05. Findings are advisory matches, not demonstrated exploits. No application dependency was upgraded or finding allowlisted in this phase.

| Area | Observed findings and next action |
| --- | --- |
| npm | 25 affected package records: Next is critical; 18 high, 5 moderate and 1 low records across the graph. Next, Axios, image-processing and build/lint dependencies require version-specific review. The current app uses App Router and remote image patterns, so server/image advisories deserve early investigation. Some Axios advisories concern Node HTTP adapters whereas the present browser client uses browser transport; do not equate every report with a reachable exploit. Development/build packages remain in audit scope. |
| Python application packages | FastAPI 0.109.0, Starlette 0.35.1, python-dotenv 1.0.0, sentence-transformers 2.3.1, transformers 4.57.6, and nltk 3.10.3 remain flagged. Final output contains 28 records but 17 distinct primary IDs. Inspect actual version-specific code paths and model/provider inputs; do not infer that a model-loader advisory is exploitable without attacker-controlled model content. Some advisories have no reported fixed version. |
| Tool corrections | The original environment supplied pip 24.2; the initial test setup used pytest 8.3.5. Audit identified pip path/extraction issues and pytest temporary-directory advisory GHSA-6w46-j5rx-g56g. Corrected only these tools to pip 26.2.1 and pytest 9.0.3, reran tests/audit, and replayed the final environment. No application package changed. |

Canonical npm audit fails on high/critical severity (`--audit-level=high`); lower findings remain visible. pip-audit fails on any finding. The owner approved temporary CI execution-step exceptions under ROADMAP DEP-01, not acceptance of any individual vulnerability. Full findings and original outcomes remain visible in dedicated advisory jobs; setup failures still fail. Public release remains blocked by unresolved applicable high/critical findings. Before public launch, review exploit prerequisites and minimum compatible fixes, add focused regressions, and run a fresh audit. Any future exception requires a specific advisory, applicability evidence, responsible owner and review/expiry condition; it must not conceal a failed advisory-service request.

The Gitleaks binary is pinned to 8.30.0 with platform archive hashes in `scripts/gitleaks.json`, obtained from upstream release metadata. Updating it requires reviewing upstream provenance, changing version/hashes together, reinstalling outside the hook, and rerunning scanner/hook tests. Official references: [Gitleaks release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.0), [pip-audit](https://github.com/pypa/pip-audit), [pytest advisory](https://github.com/advisories/GHSA-6w46-j5rx-g56g). Action pins similarly require upstream SHA verification and workflow review; no automatic merging is configured.


## APP-01 / APP-02 scoped security review

2026-10-05: independent read-only `security_reviewer` reviewed the implemented diff, session/profile routes, service ownership, localStorage, Axios behavior, request logging and contract tests. No introduced security finding blocks these contracts from becoming blocking tests. This is not public-release approval or a full authentication review.

- Body-only session lookup rejects query transport and unknown IDs without creating users. Existing persisted IDs are authoritative. Malformed bodies return validation errors without persistence; session request errors are sanitized before browser logging, and session/profile server errors omit raw exception details. Default FastAPI validation responses can echo submitted invalid input to the requester; they must not be logged as credentials by middleware/proxies.
- **SEC-01, verified source issue, Medium severity/high confidence, unresolved:** other endpoints still put bearer-like identifiers into URL paths that application middleware logs. Anyone obtaining an identifier can replay it; localStorage and missing expiry/revocation remain unchanged. The lookup endpoint's rejection of unknown IDs does not change get-or-create behavior on other routes. These remain before-public-exposure work.
- **SEC-04, design concern, Low severity/high confidence, unresolved:** automatic HTTP retries can repeat new-session creation after a lost response, and the user service commits user/profile separately. Same-module concurrent initialization is deduplicated, but cross-tab/server idempotency and atomic creation remain separate remediation.
- No schema migration, account framework, credential change, dependency-policy change or recommendation algorithm change. Profile responses preserve score maps and omit embeddings.

The reviewer independently ran 23 backend contract cases and the then-current 11 frontend wrapper cases successfully; the final ledger includes an additional interceptor log-redaction test. Deployed logs/proxies, HTTPS, browser behavior and cross-tab races were not verified. See [verification](testing.md#core-contract-remediation-app-01--app-02).
