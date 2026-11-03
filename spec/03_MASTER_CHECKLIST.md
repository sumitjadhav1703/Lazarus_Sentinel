# Master blueprint checklist

Dated **2026-11-02**. One item per BP row in the [audit](01_BLUEPRINT_IMPLEMENTATION_AUDIT.md); status/evidence there are authoritative for this snapshot. The [gated plan](02_NEXT_STAGE_PLAN.md) chooses bounded next work; this list does not authorize executing every unchecked item.

Checked means `IMPLEMENTED` for its stated scope or `NOT_APPLICABLE` because it is an explicit non-goal. Partial, blocked, superseded technology choices and future ideas remain unchecked. A checked declaration-context capability does not mean effective authorization, and a checked evidence hash does not prove semantic correctness.


- [x] **BP-001** `IMPLEMENTED` / `MVP` — Defensive read-only informational product.
- [x] **BP-002** `IMPLEMENTED` / `MVP` — Snapshot authorization and scope.
- [ ] **BP-003** `PARTIAL` / `MVP` — Repository URL/local path, commit SHA and branch identity.
- [ ] **BP-004** `PARTIAL` / `MVP` — Safe file inventory and language/framework detection.
- [x] **BP-005** `IMPLEMENTED` / `MVP` — Exclude irrelevant artifacts and redact prompt/log content.
- [ ] **BP-006** `PARTIAL` / `MVP` — Persist analysis configuration and tool versions.
- [ ] **BP-007** `BLOCKED` / `MVP` — Authorized local repository/upload intake.

- [ ] **BP-008** `BLOCKED` / `TECH` — Prove Joern on representative Python/FastAPI files.

- [x] **BP-009** `IMPLEMENTED` / `MVP` — One primary deterministic extraction adapter.
- [x] **BP-010** `IMPLEMENTED` / `MVP` — Modules/imports/function definitions and source ranges.

- [ ] **BP-011** `PARTIAL` / `FUTURE` — Class/type/member/inheritance semantics.

- [ ] **BP-012** `PARTIAL` / `MVP` — Parameters/return values/variable definitions and references.
- [ ] **BP-013** `NOT_IMPLEMENTED` / `MVP` — Selected control-flow relationships.
- [ ] **BP-014** `NOT_IMPLEMENTED` / `MVP` — Selected data-flow/dependence relationships.
- [x] **BP-015** `IMPLEMENTED` / `MVP` — Resolved and unresolved cross-module calls.

- [ ] **BP-016** `NOT_IMPLEMENTED` / `FUTURE` — Third-party dependency/version/use model.

- [x] **BP-017** `IMPLEMENTED` / `MVP` — FastAPI endpoints/HTTP methods/handler mapping.
- [ ] **BP-018** `PARTIAL` / `MVP` — Route parameters and middleware/dependency chains.
- [ ] **BP-019** `PARTIAL` / `MVP` — Service/repository/database/storage application entities.

- [ ] **BP-020** `NOT_IMPLEMENTED` / `FUTURE` — External clients/queues/internal service relationships.

- [ ] **BP-021** `PARTIAL` / `MVP` — Authentication provider/role/permission/policy identities.
- [ ] **BP-022** `NOT_IMPLEMENTED` / `MVP` — Input serialization/validation and output-handling semantics.

- [ ] **BP-023** `NOT_IMPLEMENTED` / `FUTURE` — Safe configuration/deployment/environment relationships.

- [ ] **BP-024** `NOT_IMPLEMENTED` / `MVP` — Security identity/role/ownership graph.
- [ ] **BP-025** `PARTIAL` / `MVP` — Sensitive asset classification with provenance.
- [ ] **BP-026** `NOT_IMPLEMENTED` / `MVP` — Versioned trust zones and crossing relationships.
- [ ] **BP-027** `PARTIAL` / `MVP` — Typed context-appropriate security controls.
- [ ] **BP-028** `NOT_IMPLEMENTED` / `MVP` — Sources/sinks and relevant value binding.
- [x] **BP-029** `IMPLEMENTED` / `MVP` — Observed/inferred/unknown control distinction.
- [x] **BP-030** `IMPLEMENTED` / `MVP` — Stable normalized node IDs and edge types.
- [ ] **BP-031** `PARTIAL` / `MVP` — Proposed graph vocabulary represented semantically.
- [x] **BP-032** `IMPLEMENTED` / `MVP` — File/range/analyzer/rule provenance.
- [x] **BP-033** `IMPLEMENTED` / `MVP` — Snapshot-specific reproducible graph persistence.
- [ ] **BP-034** `PARTIAL` / `MVP` — Raw analyzer outputs retained separately.
- [x] **BP-035** `IMPLEMENTED` / `MVP` — Coverage exclusions/parse failures/unresolved constructs visible.
- [x] **BP-036** `IMPLEMENTED` / `MVP` — Sensitive endpoint-to-operation evidence path.
- [ ] **BP-037** `NOT_IMPLEMENTED` / `MVP` — R1 sensitive source-to-sink flow detector.
- [ ] **BP-038** `PARTIAL` / `MVP` — R2 authorization relationship/coverage detector.
- [ ] **BP-039** `NOT_IMPLEMENTED` / `MVP` — R3 trust-boundary handling detector.
- [x] **BP-040** `IMPLEMENTED` / `MVP` — Define three rule specifications before prompts.
- [ ] **BP-041** `PARTIAL` / `MVP` — Rule prerequisites/controls/exceptions/blind spots/regressions.
- [x] **BP-042** `IMPLEMENTED` / `MVP` — Deterministic graph paths and rule checks.
- [x] **BP-043** `IMPLEMENTED` / `MVP` — Candidate finding evidence/impact/unknowns/review advice.
- [ ] **BP-044** `PARTIAL` / `MVP` — Runtime evidence review can accept/reject/downgrade with reasons.
- [x] **BP-045** `IMPLEMENTED` / `MVP` — Severity and confidence independent.
- [ ] **BP-046** `NOT_IMPLEMENTED` / `MVP` — Transparent multidimensional risk ranking.

- [ ] **BP-047** `SUPERSEDED` / `TECH` — LangGraph stateful parallel orchestration.

- [ ] **BP-048** `PARTIAL` / `MVP` — Repository Analyst role and structured manifest.
- [x] **BP-049** `IMPLEMENTED` / `MVP` — Graph Analyst role/validated graph contract.
- [ ] **BP-050** `PARTIAL` / `MVP` — Architecture Analyst role/application facts.
- [ ] **BP-051** `PARTIAL` / `MVP` — Security Analyst role/control/data/identity facts.
- [ ] **BP-052** `PARTIAL` / `MVP` — Threat Analyst role/schema-grounded hypotheses.
- [ ] **BP-053** `NOT_IMPLEMENTED` / `MVP` — Evidence Reviewer specialist role.
- [x] **BP-054** `IMPLEMENTED` / `MVP` — Report Agent responsibility.
- [ ] **BP-055** `PARTIAL` / `MVP` — Shared state including review results/security assets.
- [x] **BP-056** `IMPLEMENTED` / `MVP` — Schema validate reasoning IDs/evidence and reject fabrications.
- [x] **BP-057** `IMPLEMENTED` / `MVP` — Minimal bounded model subgraphs and evidence.
- [ ] **BP-058** `PARTIAL` / `MVP` — Workflow idempotence/resume without duplicates.
- [ ] **BP-059** `PARTIAL` / `MVP` — Record contradictions and alternative explanations.
- [x] **BP-060** `IMPLEMENTED` / `MVP` — LLM sidecars cannot mutate canonical findings/graph; citations constrained; prose remains UNREVIEWED and can be wrong.
- [ ] **BP-061** `PARTIAL` / `MVP` — Meta adapter and provider provenance.
- [ ] **BP-062** `BLOCKED` / `MVP` — Live Meta meaningful reasoning verified.
- [ ] **BP-063** `PARTIAL` / `MVP` — Core overview screen.
- [x] **BP-064** `IMPLEMENTED` / `MVP` — Interactive graph/path navigation.
- [ ] **BP-065** `PARTIAL` / `MVP` — Filters by node type/risk/confidence/coverage.
- [x] **BP-066** `IMPLEMENTED` / `MVP` — Finding details with evidence and uncertainty.
- [x] **BP-067** `IMPLEMENTED` / `MVP` — Coverage/unknowns screen.
- [ ] **BP-068** `PARTIAL` / `MVP` — Navigate finding to path to actual source lines.
- [ ] **BP-069** `PARTIAL` / `MVP` — Display analyzed commit and analysis version.
- [x] **BP-070** `IMPLEMENTED` / `MVP` — Structured JSON and human-readable export.

- [ ] **BP-071** `SUPERSEDED` / `TECH` — HTML/PDF report export.
- [ ] **BP-072** `SUPERSEDED` / `TECH` — HTTP FastAPI backend service.
- [x] **BP-073** `IMPLEMENTED` / `TECH` — React/Vite visualization.
- [x] **BP-074** `IMPLEMENTED` / `TECH` — NetworkX graph integration.
- [x] **BP-075** `IMPLEMENTED` / `TECH` — SQLite/JSON persistence.

- [x] **BP-076** `IMPLEMENTED` / `MVP` — Modular analyzer-neutral adapter interface.
- [ ] **BP-077** `PARTIAL` / `MVP` — Resource-limited analysis worker.
- [x] **BP-078** `IMPLEMENTED` / `MVP` — No target code/build/dependency execution.
- [ ] **BP-079** `BLOCKED` / `MVP` — Read-only OS mounts/filesystem and restricted network.
- [ ] **BP-080** `PARTIAL` / `MVP` — Least privilege/separate worker boundaries.
- [x] **BP-081** `IMPLEMENTED` / `MVP` — Secret prevention in model context/exported artifacts.
- [ ] **BP-082** `PARTIAL` / `MVP` — Audit tool invocations/timeouts/policy decisions.
- [x] **BP-083** `IMPLEMENTED` / `MVP` — Controlled synthetic repository with known safe/weak/unknown cases.
- [ ] **BP-084** `PARTIAL` / `MVP` — Seeded recall/false-candidate measurement.
- [x] **BP-085** `IMPLEMENTED` / `MVP` — Path reconstruction/evidence completeness evaluation.
- [ ] **BP-086** `PARTIAL` / `MVP` — Repository/endpoint/unknown coverage metrics.
- [x] **BP-087** `IMPLEMENTED` / `MVP` — Analysis duration/repeatability measurement.
- [ ] **BP-088** `NOT_IMPLEMENTED` / `MVP` — Established tool vs context vs combined comparison.
- [x] **BP-089** `IMPLEMENTED` / `MVP` — End-to-end known-ground-truth candidate demonstration.

- [ ] **BP-090** `NOT_IMPLEMENTED` / `FUTURE` — User/human review triage and feedback persistence.
- [ ] **BP-091** `NOT_IMPLEMENTED` / `FUTURE` — Incremental Git updates and graph/commit comparison.
- [ ] **BP-092** `NOT_IMPLEMENTED` / `FUTURE` — Dependency/advisory and secret scanners.
- [ ] **BP-093** `NOT_IMPLEMENTED` / `FUTURE` — Additional frameworks/custom rule adapters.
- [ ] **BP-094** `PARTIAL` / `FUTURE` — CI/repository integration.
- [ ] **BP-095** `NOT_IMPLEMENTED` / `FUTURE` — C/C++ memory-safety pack.
- [ ] **BP-096** `NOT_IMPLEMENTED` / `FUTURE` — JavaScript/TypeScript target analyzer.
- [ ] **BP-097** `NOT_IMPLEMENTED` / `FUTURE` — IaC/cloud IAM graph.
- [ ] **BP-098** `NOT_IMPLEMENTED` / `FUTURE` — Authorized runtime evidence integration.
- [ ] **BP-099** `NOT_IMPLEMENTED` / `FUTURE` — Business-logic/abuse-case policy modeling.
- [ ] **BP-100** `NOT_IMPLEMENTED` / `FUTURE` — Continuous/historical graph and advanced slicing.
- [ ] **BP-101** `NOT_IMPLEMENTED` / `FUTURE` — Enterprise/multi-user collaboration/storage scale.

- [ ] **BP-102** `BLOCKED` / `EVENT` — Event eligibility/track/portal deliverable confirmation.
- [ ] **BP-103** `BLOCKED` / `EVENT` — License and submission receipt.
- [ ] **BP-104** `PARTIAL` / `EVENT` — Demo technical docs/screenshots/recording package.

- [x] **BP-105** `IMPLEMENTED` / `BOUNDARY` — No complete-graph/exhaustive-security/novel-CPG claims.

- [x] **BP-106** `NOT_APPLICABLE` / `NON_GOAL` — Autonomous exploitation/remediation/arbitrary network attacks.
- [x] **BP-107** `NOT_APPLICABLE` / `NON_GOAL` — Multiple initial scanners/distributed graph database.

No product tests were rerun for this documentation-only inventory. Blockers and research ideas remain open; the accepted bounded demo is not reopened.
