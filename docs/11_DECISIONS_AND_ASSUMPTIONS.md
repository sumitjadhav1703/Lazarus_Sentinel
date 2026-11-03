# 11 — Decisions, assumptions and open gates

> Team/platform update (2026-11-02): [team handoff](21_TEAM_HANDOFF.md), [finite next-phase plan](22_NEXT_PHASE_PLAN.md), and [current portability/publication evidence](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) supersede earlier onboarding, remote-state and platform assumptions. Historical checks below retain their original date and scope.


## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

At this 2026-11-02 checkpoint, the recorded milestones were baseline `7797b85`, integrated demo `4f0346c`, and viewer refinement `2cda191`. The demo ran offline. The later [competition verification](../spec/06_COMPETITION_VERIFICATION.md) records the live Meta result, public Pages deployment, and separate controlled DATA, TRUST, and actor/action/resource reports. Fixed synthetic intake remains the supported scope.

Updated 2026-11-02. Approved current scope is in [document 13](13_FIRST_SLICE_CONTRACT.md); verified behavior in [document 14](14_IMPLEMENTATION_REVIEW.md). [Document 15](15_NEXT_STEPS.md) contains recommendations, not newly accepted implementation decisions.

## Decision register — preserve identity and scope

| ID | Decision | Current interpretation |
|---|---|---|
| D-001 | Graph-first application-security product, not a generic chatbot | Product objective retained; evidence correlation is the value proposition |
| D-002 | Code, application and security-context layers | Target model; only emitted facts/policy context are claimed today |
| D-003 | Reuse analyzers rather than write a universal compiler | AST structure adapter now; no substitute taint compiler |
| D-004 | Joern candidate subject to Python/FastAPI measurement | NOT_ATTEMPTED, not rejected; optional next spike N09 |
| D-005 | AST fallback with honest limitations | Approved primary first-slice structure path; no CPG/data-flow claim |
| D-006 | NetworkX + SQLite + portable JSON | Implemented MultiDiGraph, scans/findings/artifact refs and JSON/Markdown |
| D-007 | React/Vite + Cytoscape.js frontend direction | Implemented fixed artifact viewer; see document 16 |
| D-008 | LangGraph only when its state/concurrency adds value | Deferred; D-018 uses linear Python now |
| D-009 | Meta/Muse Spark intended hackathon runtime provider | Access, event suitability and privacy/request gates unverified; disabled today |
| D-010 | Model explains evidence rather than establishes facts | Implemented explanation boundary; mock is offline, live access blocked |
| D-011 | Defensive static read-only product | No exploitation, target execution, automatic fixes or external scans |
| D-012 | AGENTS.md instructions separate from AGENT.md ledger | Retained; append-only session history preserved |
| D-013 | Bounded independent sub-agents with file ownership | Used for implementation, review and documentation |
| D-014 | Evidence-first fixture-only delivery | Owner approved after EGM/Astra review; completed |
| D-015 | AST now; Joern NOT_ATTEMPTED | Local Joern absent at inventory, no compatibility failure invented |
| D-016 | LS-AUTH-001 only; data/trust NOT_IMPLEMENTED | LOW-confidence declaration-gap candidates; opaque scopes diagnostic-only |
| D-017 | Exact scanned-byte manifest is authoritative | Includes policy identity; dirty/no-Git content cannot masquerade as clean commit |
| D-018 | Linear CLI/report workflow; no live egress | Historical first-slice cut line; document 16 adds fixed UI and optional provider adapter, leaving HTTP API/LangGraph deferred |
| D-019 | Local CPython 3.13.14 + locked Pydantic/NetworkX | Implemented local environment and backend/uv.lock; no global installs |
| D-020 | Process caps are not an OS hostile-repository sandbox | Only controlled local fixture approved; broader intake needs N14/N15 |

## Resolved first-session questions

- Repository exists with backend package/tests, synthetic fixture/oracle and docs; initial documentation-only discovery is complete. No `.git` directory has been initialized.
- Last observed machine/tool inventory is dated in AGENT.md; do not rerun all setup or silently treat historical versions as freshly measured.
- Astra/Sol delegated execution was exercised; Terra is available as a runtime choice but was not used for this backend slice. Coordinator display identity was not exposed.
- Supported FastAPI subset, opaque control behavior, byte evidence and CLI contract are frozen in document 13 and tested. The fixture graph/report pipeline is complete.
- Last verified baseline: 73 tests; 6 endpoints, 23 nodes, 36 edges, 2 LOW candidates and 3 matching declarations; expected PARTIAL coverage. This is not generalized detector accuracy.

## Remaining external facts and product choices

| Gate | Status / next action |
|---|---|
| Event acceptance, complete rules, team/track, required Meta usage | Owner-only portal facts unverified; N01 |
| Public deadline | Official page reopened Nov 2: Nov 4, 9:00 PM ET = Nov 5, 7:30 AM IST; may change |
| Actual Meta account/model access, quota, privacy/spend approval | Not verified by public documentation; N02/N08 |
| License, Git baseline, publication/deployment | Baseline 7797b85 preserved; Apache-2.0 chosen 2026-11-03 (D-031); remote actions require separate selection |
| Next demo contract and team allocation | Contract frozen and fixed viewer implemented; no second human teammate assumed; N05/N06 |
| Joern/value-flow capability and trust policy | No measurements/implemented families; N09/N10 |
| Arbitrary-repository isolation/intake | Not approved or implemented; N14/N15 before expansion |

## Proposed follow-on choices — not new accepted decisions

R-001: resolve submission/provider requirements early and preserve the offline product independently of eligibility. R-002: fixed validated synthetic artifact viewer before HTTP/scan controls. R-003: optional explanation contract/mock before gated live Meta; schema-valid prose still needs review. R-004: timebox analyzer experiments and leave unsupported detectors explicit rather than consume demo buffer. R-005: local Git commit supplements content evidence; publication is separate. Astra reviewed this ordering; owner approved the bounded integrated increment in D-021; further expansion still requires selection.

## Risks and stopping conditions

- Unknown/opaque controls can hide real problems; keep diagnostics and never label recognized declarations secure.
- Process/output prechecks do not protect against hostile concurrent filesystem changes; no arbitrary target expansion without a new isolation review.
- Valid evidence IDs do not establish factual model prose; keep facts immutable, review shown narrative, retain disabled/offline fallback.
- Provider/event access may block submission suitability while local software still works; record that distinction honestly.
- Avoid unfinished stack scaffolding: no obligatory API, LangGraph, new detector, database service or swarm just to match the original diagram.
- Keep measured revision/path evidence and independently review trust-boundary changes. Do not multiply severity, confidence and coverage into an unexplained score.

## Rejected or deferred directions

No universal compiler, complete-graph promise, automatic exploit validation/remediation, multi-language first increment, distributed graph database or microservice deployment without measured need. N14–N18 retain the longer-term analysis, intake, operational and platform backlog without pretending it is currently delivered.

## Integrated demo decisions — approved 2026-11-02

- **D-021:** Owner selected demo-first then staged expansion and authorized implementation of the reviewed parallel plan. docs/16_DEMO_DELIVERY_CONTRACT.md is the frozen next-increment contract; document13 remains the original analyzer baseline.
- **D-022:** Export a new immutable trusted-synthetic bundle from read-only committed references, preserving canonical graph0.1.0 and validating mirrors/source. Viewer has no arbitrary upload/path/API requirement; bundlecap1MiB/500nodes/2000edges.
- **D-023:** Explanations are separately bound immutable annotations, disabled by default. Standard MuseSpark1.3,1024 outputtokens,20s absolutedeadline,16KiBcontext/32KiBresponse,oneattempt,no redirects/retries/tools. Transactional ledgerUSD3/fiveattemptsglobaldemo; ambiguous outcome retains reservation and blocks more calls. Budget follows owner'sUSD3–4 range conservatively; no key present and no livecall implied by mock success.
- **D-024:** Local Git baseline7797b85 and feat/integrated-demo branch created using existing Git identity; no remote, license selection or publication. Reviewed fixed synthetic assets may be bundled for offline clean-checkout UI.
- **D-025:** Optional analyzer/isolation/research deliverables must report actual measured gates. N18 firsttranche catalogs alltopics and evaluates DATA/TRUST; it does not falsely close open-ended implementation families. Broader intake remains behind tested OS isolation.


### D-026 — Viewer comprehension and truthful navigation (2026-11-02)

Owner selected all three audiences: first-time/demo, developer and security reviewer. Refine the existing visual identity with a guided exact path, explicit full-graph view, endpoint search and node-level evidence. Keep candidate path identities separate from declaration relationships. A noncandidate endpoint is “No candidate in this scan,” never a safe/security label. Astra approved these constraints and accepted the implementation read-only. Details and verification are in document20. No backend, provider, intake or detector contract changes.


### D-027 — Team handoff and bounded native portability (2026-11-02)

Owner authorized public repository publication and macOS/Windows support. Preserve canonical AGENT.md across case-insensitive platforms; AGENTS.md shared rules and CLAUDE.md entry point serve both agents. Retain POSIX no-follow/resource controls; Windows uses explicit reparse rejection, bounded binary identity checks, spawn and byte-range writer locks, with no OS-isolation equivalence claim. Native Windows/macOS/Linux setup/tests/build passed for06f993e; strict canonical POSIX artifact/snapshot identities are unchanged. P01/P02 complete; future account/intake/license/remote-service decisions remain gated. See document23 for original failures, repairs and primary job evidence.

### D-028 — Bounded value provenance experiment (2026-11-03)

Use a standalone standard-library AST experiment to test local assignment provenance against a fixed synthetic oracle. Owner approved an independent fallback review for this increment after Astra routing could not be verified. The result is research evidence for the documented syntax subset. Production graph schema, policy and detector acceptance require their own review. See [contract and measured results](../spec/04_CONTROLLED_SEMANTIC_EXPERIMENT.md).


### D-029 — Opt-in LangGraph demo orchestration (2026-11-03)

Keep the default linear scanner and published recording. Add a pinned optional LangGraph extra for the fixed rehearsal stages, with tracing disabled and the existing Meta ledger unchanged. Durable review and pause/resume require a separate design and replay checks. The live competition recording predates this optional integration.


### D-030 — Read-only agent investigation with a separate ledger (2026-11-03)

The owner approved building an offline Muse Spark investigation loop over the committed graph. It uses a separate agent ledger capped at 20 calls and USD 1. The shared USD 3 / five-attempt explanation ledger is unchanged. The tools are pure graph lookups. No source text is sent. Every recorded step is replayed on bundle validation. Citations must come from tool results for the investigated finding. Any malformed turn fails the run with no retry and no partial record. The output is UNREVIEWED notes, never a verdict. The live run waits for owner-approved Astra or a fallback review and explicit owner authorization. See [agent investigation](../spec/10_AGENT_INVESTIGATION.md).


### D-031 — Apache-2.0 license (2026-11-03)

The owner chose the Apache License 2.0 for the repository (issue #40). `LICENSE` holds the unmodified text from GitHub's license API. `NOTICE` names "Sumit Jadhav and Lazarus Sentinel contributors". Contributions are accepted under the same terms. Teammates listed on the event entry should agree to this choice. Third-party dependencies keep their own licenses.


### D-032 — Weakness references and bounded web search (2026-11-03)

Each rule carries a reviewed static mapping to public weakness categories; `LS-AUTH-001` maps to CWE-862 and OWASP A01:2025. The mapping is a category label, not evidence. An optional Meta `web_search` refresh sends only a fixed question and keeps only allowlisted https citations. It settles search fees on the agent ledger and fails closed. Its live run shares the D-030 review and authorization gate.
