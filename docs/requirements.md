# Product requirements and open decisions

## Status and scope

The owner confirmed **private development toward a later public launch**. Mavilon helps people discover movies and anime through browsing, search, mood recommendations, details, saved favorites, and a personalized profile. This purpose is observed in the application; audience segments, business model, launch date, and service targets have not been specified.

The approved foundation phase adds development context, reproducibility, tests, and local/CI safeguards. It preserves application functionality and existing package versions unless a verified compatibility/security issue justifies a separate, explained change. Defect remediation is a separate phase. Public launch is not approved.

The following matrix distinguishes observed implementation from **proposed remediation acceptance criteria**. Those criteria guide discussion and test design; they are not evidence of working behavior or authority to implement changes in this phase.

| Journey | Observed implementation | Proposed acceptance criteria for remediation |
| --- | --- | --- |
| Discover and search | Home includes movie/anime selection, trending, search, and mood recommendations; TMDB supplies both content types. | Search returns the latest query's results; loading, empty, provider failure, and retry are distinguishable. Switching content type does not show stale results. |
| Inspect content | Cards open details and similar-content results, with trailer links where available. | Valid IDs show matching metadata; missing/invalid IDs and provider failure produce deliberate states; similar-item failure is distinguishable from no matches. Keyboard focus and dismiss behavior are verified. |
| Return to a session | Browser localStorage stores an anonymous identifier used in API paths. The existing-session JSON request does not match the backend's query parameter. | A returning session preserves its data without creating another user; malformed/unknown identity follows an agreed policy. Identity privacy requirements below must be resolved first. |
| Save/remove favorites | Favorites persist server-side with a per-user/content uniqueness constraint; the UI updates optimistically. Failure rollback is incomplete. | Repeated save/remove is safe; successful state survives refresh; a failed write restores or refetches authoritative state and gives usable feedback. |
| Inspect taste | Interactions update a movie taste embedding and scored genre/mood dictionaries. API response typing and frontend expectations disagree; anime updates are unfinished. | Populated/empty profiles conform to one shared contract; the UI distinguishes failure from no data. Movie/anime support and explanation wording match verified capability. |
| Inspect/remove history | Profile reads `watch_history`; interaction recording writes `interactions`. The normal interaction path does not populate watch history. | Decide what constitutes history before implementing it. Deletion and recalculation reflect that decision, with truthful failure/retry behavior. |
| Chat | Rule/keyword parsing retrieves recommendations; no external LLM integration was identified. | Unsupported requests and unavailable recommendations are explained truthfully; queries and response sizes are bounded. Avoid promising general conversational intelligence. |
| Degraded operation | Model loading and provider requests can fail; fallback paths contain known defects. | Agreed provider/model degradation behavior is exercised explicitly; success is never fabricated when a dependency fails. |

## Decisions required before affected remediation

1. **Identity:** retain anonymous browser sessions, add accounts, or support both? Define expiration/revocation, recovery after storage loss, and acceptable data isolation. Current behavior is not the security policy.
2. **History:** mean actual watched content, details/trailer views, or recommendation interactions? Define the event, deduplication, retention, and effect of deletion on personalization. The UI currently makes inconsistent promises.
3. **Personalization:** which events and content types influence taste? Define cold-start behavior and a small human-reviewed relevance set. Numerical score determinism alone does not prove recommendation quality.
4. **Privacy:** define disclosure, consent where applicable, retention, deletion, and operational access to behavioral data. Do not invent legal requirements without launch markets and processing context.
5. **Degradation and delivery:** choose expected provider/model failure behavior, hosting, CPU/GPU needs, data ownership, operating owner, and realistic availability/latency targets before release planning.

These decisions do not block foundation-only work. Identity/history decisions block their respective behavior changes; operational/privacy decisions block public release readiness.

## Exclusions from the current phase

No application defect fixes, UI redesign, dependency modernization for its own sake, new content providers, account/payment systems, model migration, infrastructure deployment, or hosted repository setting changes. Playwright and browser automation remain deferred until journeys and expected behavior stabilize. See [ROADMAP.md](../ROADMAP.md) for ordered work and [testing.md](testing.md) for evidence.
