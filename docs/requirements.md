# Product requirements and open decisions

## Status and scope

The owner confirmed **private development toward a later public launch**. Mavilon helps people discover movies and anime through browsing, search, mood recommendations, details, saved favorites, and a personalized profile. This purpose is observed in the application; audience segments, business model, launch date, and service targets have not been specified.

The approved foundation phase adds development context, reproducibility, tests, and local/CI safeguards. It preserves application functionality and existing package versions unless a verified compatibility/security issue justifies a separate, explained change. The first separately authorized remediation phase covers only APP-01 and APP-02. Public launch is not approved.

The following matrix distinguishes observed implementation from **proposed remediation acceptance criteria**. The APP-01/APP-02 contract decisions below are authorized for this phase; other proposed criteria remain deferred.

| Journey | Observed implementation | Proposed acceptance criteria for remediation |
| --- | --- | --- |
| Discover and search | Home includes movie/anime selection, trending, search, and mood recommendations; TMDB supplies both content types. | Search returns the latest query's results; loading, empty, provider failure, and retry are distinguishable. Switching content type does not show stale results. |
| Inspect content | Cards open details and similar-content results, with trailer links where available. | Valid IDs show matching metadata; missing/invalid IDs and provider failure produce deliberate states; similar-item failure is distinguishable from no matches. Keyboard focus and dismiss behavior are verified. |
| Return to a session | Browser localStorage stores an anonymous identifier used in API paths. Session creation/lookup uses JSON and preserves the server-confirmed identity (APP-01 resolved). | A returning session preserves its identity and data without another user; invalid/unknown requests follow the APP-01 policy below. Broader identity lifecycle remains open. |
| Save/remove favorites | Favorites persist server-side with a per-user/content uniqueness constraint; the UI updates optimistically. Failure rollback is incomplete. | Repeated save/remove is safe; successful state survives refresh; a failed write restores or refetches authoritative state and gives usable feedback. |
| Inspect taste | Interactions update a movie taste embedding and scored genre/mood dictionaries. API and frontend share numeric score maps (APP-02 resolved); anime updates remain unfinished. | Populated/empty profiles conform to one shared contract; the UI distinguishes failure from no data. Movie/anime support and explanation wording match verified capability. |
| Inspect/remove history | Profile reads `watch_history`; interaction recording writes `interactions`. The normal interaction path does not populate watch history. | Decide what constitutes history before implementing it. Deletion and recalculation reflect that decision, with truthful failure/retry behavior. |
| Chat | Rule/keyword parsing retrieves recommendations; no external LLM integration was identified. | Unsupported requests and unavailable recommendations are explained truthfully; queries and response sizes are bounded. Avoid promising general conversational intelligence. |
| Degraded operation | Model loading and provider requests can fail; fallback paths contain known defects. | Agreed provider/model degradation behavior is exercised explicitly; success is never fabricated when a dependency fails. |

## Decisions required before affected remediation

1. **Identity beyond APP-01:** this phase retains anonymous browser sessions. Before public launch, decide whether to retain them, add accounts, or support both. Define expiration/revocation, recovery after storage loss, and acceptable data isolation. Current behavior is not the security policy.
2. **History:** mean actual watched content, details/trailer views, or recommendation interactions? Define the event, deduplication, retention, and effect of deletion on personalization. The UI currently makes inconsistent promises.
3. **Personalization:** which events and content types influence taste? Define cold-start behavior and a small human-reviewed relevance set. Numerical score determinism alone does not prove recommendation quality.
4. **Privacy:** define disclosure, consent where applicable, retention, deletion, and operational access to behavioral data. Do not invent legal requirements without launch markets and processing context.
5. **Degradation and delivery:** choose expected provider/model failure behavior, hosting, CPU/GPU needs, data ownership, operating owner, and realistic availability/latency targets before release planning.

These decisions do not block foundation-only work. Broader identity/history decisions block their respective future behavior changes; operational/privacy decisions block public release readiness.

## APP-01 / APP-02 contract decisions

Authorized scope: repair returning-session and populated taste-profile contracts while retaining the existing anonymous identity and scoring model.

- **APP-01:** `POST /api/users/session` accepts an optional JSON object with `session_id`. No body, `{}`, or a null ID creates a server-generated UUID session and returns `{session_id, user_id, is_new: true}`. A supplied nonempty string is an opaque identity: it must already exist, returns the same persisted IDs with `is_new: false`, and does not create users or profiles. Existing non-UUID IDs remain usable because earlier clients generated fallback IDs. Unknown IDs return 404; invalid body fields/types return 422; query parameters return 400. The lookup does not adopt arbitrary client-supplied unknown IDs.
- The frontend stores and uses the response identity. Concurrent initialization within one browser module shares a request. Only 404/422 permits clearing invalid identity and requesting a new session. Network/server failures preserve existing storage and propagate an error; failed creation never invents a fallback identity. A lost creation response can still cause another creation through existing HTTP retries; cross-tab initialization and broader mutation idempotency remain deferred.
- **APP-02:** profile responses always contain `favorite_genres: Record<string, number>`, `favorite_moods: Record<string, number>`, and `interaction_count: number`. Values are decayed frequency scores, not probabilities: existing scoring decays previous values by 0.95 and adds 1.0 for current labels. Fractional scores must survive serialization. New/missing profiles and null stored preferences return empty maps; legacy unscored lists map labels to 1.0, matching the service's existing compatibility rule. Other malformed populated values fail instead of becoming empty success. No persistence migration or scoring change is required.
- The profile UI consumes the shared type, sorts/displays scores as before, and offers a retry message on load failure. Backend deterministic HTTP/database tests and frontend wrapper tests verify contracts; browser rendering is separate evidence.

## Exclusions from the current phase

No unrelated defect fixes, UI redesign, dependency changes, favorite rollback, history semantics, anime personalization, recommendation fallback, resource limits, account systems, deployment, or hosted repository settings. Broader identity/privacy and lifecycle decisions remain public-release prerequisites. Browser automation remains deferred. See [ROADMAP.md](../ROADMAP.md) for ordered work and [testing.md](testing.md) for evidence.
