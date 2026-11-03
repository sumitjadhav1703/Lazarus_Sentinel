# Original blueprint → implementation audit

Dated **2026-11-02**. Documentation-only comparison of the owner's 33-page, version 1.0 research blueprint (01 November 2026) with reviewed source `06f993e` and documentation HEAD `9f3d021`. The private PDF/text is not reproduced or published here. Page references use printed PDF pages, not text line numbers.

**The approved fixed-fixture baseline and integrated offline demo are complete. The original three-detector blueprint MVP is not complete.** The current product performs deterministic, conservative authorization-*declaration* assessment on one synthetic FastAPI fixture. It does not prove effective authorization, data flow, trust-boundary handling or production security accuracy.

## Reading the result

`MVP` identifies a blueprint MVP behavior; `TECH` identifies a recommended implementation choice, not an unconditional requirement to adopt that package; `FUTURE` covers expansion/research; `EVENT` is an external delivery gate; `BOUNDARY` is a required claim/safety limit; `NON_GOAL` is deliberately excluded. Approved contracts in [document 13](../docs/13_FIRST_SLICE_CONTRACT.md), [document 16](../docs/16_DEMO_DELIVERY_CONTRACT.md) and the decision register control present delivery scope. Approval of a smaller contract does not erase the larger blueprint gap.

- `IMPLEMENTED`: the row's bounded behavior exists with source/test or recorded delivery evidence.
- `PARTIAL`: a real subset exists; the final column names the missing part.
- `NOT_IMPLEMENTED`: no executable product capability is established.
- `BLOCKED`: a documented prerequisite/external gate prevents proceeding; not a completed item.
- `SUPERSEDED`: an approved alternative replaces a technology/format for current delivery only; not evidence that the original choice was implemented.
- `NOT_APPLICABLE`: explicit non-goal, not unfinished implementation.

Rows are independently auditable obligations, not equal engineering effort. Some related obligations deliberately overlap (for example the detector and its evidence contract). **Counts describe this catalogue, not percent of product completed, code coverage, security coverage or estimated remaining effort.** Future ideas and non-goals must not inflate the MVP denominator.

## Evidence index

Paths below are repository-relative, linked from this file. These establish implementation and existing measurements; this audit did not rerun application tests or external services.

| Ref | Source and verification evidence |
|---|---|
| E1 | [intake.py](../backend/src/lazarus_sentinel/intake.py), [test_intake.py](../backend/tests/test_intake.py), [cli.py](../backend/src/lazarus_sentinel/cli.py) |
| E2 | [service.py](../backend/src/lazarus_sentinel/service.py), [test_service.py](../backend/tests/test_service.py), [test_acceptance.py](../backend/tests/test_acceptance.py) |
| E3 | [analysis.py](../backend/src/lazarus_sentinel/analysis.py), [models.py](../backend/src/lazarus_sentinel/models.py), [test_analysis.py](../backend/tests/test_analysis.py) |
| E4 | [rules.py](../backend/src/lazarus_sentinel/rules.py), [test_rules.py](../backend/tests/test_rules.py), [test_models.py](../backend/tests/test_models.py) |
| E5 | [report.py](../backend/src/lazarus_sentinel/report.py), [viewer](../frontend/src/main.tsx), [graph UI](../frontend/src/Network.tsx), [frontend tests](../frontend/src/main.test.tsx), [UI evidence](../docs/20_VIEWER_CLARITY_AND_DESIGN.md) |
| E6 | [explanations.py](../backend/src/lazarus_sentinel/explanations.py), [meta_provider.py](../backend/src/lazarus_sentinel/meta_provider.py), [budget.py](../backend/src/lazarus_sentinel/budget.py), [explanation tests](../backend/tests/test_explanations.py), [provider tests](../backend/tests/test_meta_provider.py) |
| E7 | [persistence.py](../backend/src/lazarus_sentinel/persistence.py), [bundle.py](../backend/src/lazarus_sentinel/bundle.py), [persistence tests](../backend/tests/test_persistence.py), [bundle tests](../backend/tests/test_bundle.py), [inspector](../scripts/inspect_artifacts.py) |
| E8 | [worker.py](../backend/src/lazarus_sentinel/worker.py), [test_worker.py](../backend/tests/test_worker.py) |
| E9 | [first contract](../docs/13_FIRST_SLICE_CONTRACT.md), [demo contract](../docs/16_DEMO_DELIVERY_CONTRACT.md), [rule specifications](../docs/04_ANALYSIS_RULES.md), [decisions](../docs/11_DECISIONS_AND_ASSUMPTIONS.md) |
| E10 | [capability/research report](../docs/17_CAPABILITY_AND_RESEARCH_REPORT.md) — measured Joern/sandbox blockers and DATA/TRUST prerequisites |
| E11 | [evaluation](../docs/18_DEMO_EVALUATION.md), [integrated review](../docs/19_INTEGRATED_DEMO_REVIEW.md), [variant tests](../backend/tests/test_evaluation_variants.py) |
| E12 | [team handoff](../docs/21_TEAM_HANDOFF.md), [next-phase plan](../docs/22_NEXT_PHASE_PLAN.md), [native/publication evidence](../docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md) |

Latest recorded checks: **139 backend passes plus one Windows-only skip on local macOS; 16 frontend tests; native Windows/macOS/Linux CI passed.** These are recorded source checks, not fresh tests for this audit. The fixture has six supported endpoints, 23 nodes, 36 edges and two LOW-confidence candidate declaration gaps. Live Meta calls: **zero**. The fixed viewer loads packaged validated artifacts; it is not a live HTTP analysis service.

## Requirement catalogue

Evidence codes resolve in the table above. Every BP ID has exactly one matching item in the [master checklist](03_MASTER_CHECKLIST.md).

| ID | Blueprint obligation (paraphrased) | Class | Status | PDF pages | Evidence and boundary |
|---|---|---|---|---|---|
| BP-001 | Defensive read-only informational product | MVP | IMPLEMENTED | 2–4,21,29 | Intake/CLI restrict the fixed owned fixture; no exploit or patch action. [E1,E2]. |
| BP-002 | Snapshot authorization and scope | MVP | IMPLEMENTED | 16,21,28 | Exact fixture ID allowlist, not authorization for arbitrary repositories [E1]. |
| BP-003 | Repository URL/local path, commit SHA and branch identity | MVP | PARTIAL | 9,12,28 | Content-derived revision and root label exist; analyzed fixture is not captured as a Git URL/commit/branch [E1,E3]. |
| BP-004 | Safe file inventory and language/framework detection | MVP | PARTIAL | 16,23,28 | Bounded manifest and Python/FastAPI profile; no general framework discovery [E1,E3]. |
| BP-005 | Exclude irrelevant artifacts and redact prompt/log content | MVP | IMPLEMENTED | 16,21,28 | Fixed manifest, metadata/hash evidence, redacted bounded explanation context [E1,E6]. |
| BP-006 | Persist analysis configuration and tool versions | MVP | PARTIAL | 17,28 | Analyzer/rule/schema/provider provenance exists; no complete general repository/tool-environment manifest [E3,E6,E7]. |
| BP-007 | Authorized local repository/upload intake | MVP | BLOCKED | 23–24 | Only fixture:fastapi-demo; broader intake waits for measured isolation [E1,E10]. |
| BP-008 | Prove Joern on representative Python/FastAPI files | TECH | BLOCKED | 3,6,25,28,31 | Setup blocked: absent executable and compatible pinned JDK; analysis NOT_ATTEMPTED, not failed [E10]. |
| BP-009 | One primary deterministic extraction adapter | MVP | IMPLEMENTED | 3,6,17,21 | Python AST adapter is approved bounded alternative under D-014–D-020; not a CPG [E3,E9]. |
| BP-010 | Modules/imports/function definitions and source ranges | MVP | IMPLEMENTED | 9,28 | Supported fixture syntax extracted with source evidence [E3]. |
| BP-011 | Class/type/member/inheritance semantics | FUTURE | PARTIAL | 9 | CLASS and nested FUNCTION declarations plus CONTAINS extraction exist; inheritance, type resolution and broader member semantics do not. The packaged fixture contains no classes [E3]. |
| BP-012 | Parameters/return values/variable definitions and references | MVP | PARTIAL | 9 | Functions/calls extracted; no semantic value identity, def-use or return-flow model [E3,E10]. |
| BP-013 | Selected control-flow relationships | MVP | NOT_IMPLEMENTED | 5,9,23,28 | AST containment/calls are not a CFG [E3,E10]. |
| BP-014 | Selected data-flow/dependence relationships | MVP | NOT_IMPLEMENTED | 5,9,13,23,28 | No PDG or measured value/taint edges; CALLS is not FLOWS_TO [E3,E10]. |
| BP-015 | Resolved and unresolved cross-module calls | MVP | IMPLEMENTED | 9,12,28 | Conservative supported static calls and unresolved diagnostics [E3]. |
| BP-016 | Third-party dependency/version/use model | FUTURE | NOT_IMPLEMENTED | 9,14,24 | Project lockfiles are not target dependency/advisory analysis [E3,E10]. |
| BP-017 | FastAPI endpoints/HTTP methods/handler mapping | MVP | IMPLEMENTED | 10,23,28 | Literal supported declaration subset; six baseline endpoints; dynamic registration unknown [E3,E11]. |
| BP-018 | Route parameters and middleware/dependency chains | MVP | PARTIAL | 10 | Literal dependency declarations modeled conservatively; no full parameter/middleware execution semantics [E3]. |
| BP-019 | Service/repository/database/storage application entities | MVP | PARTIAL | 10,18 | Fixture functions represent layers and protected operations; no extracted DATABASE/data-model semantics [E3,E11]. |
| BP-020 | External clients/queues/internal service relationships | FUTURE | NOT_IMPLEMENTED | 10 | No service-client/message semantic adapter [E3,E10]. |
| BP-021 | Authentication provider/role/permission/policy identities | MVP | PARTIAL | 10,14 | Human protected-operation policy and named dependency declarations; no effective identity/permission binding [E3,E4]. |
| BP-022 | Input serialization/validation and output-handling semantics | MVP | NOT_IMPLEMENTED | 10,13 | No context-appropriate value/control model [E10]. |
| BP-023 | Safe configuration/deployment/environment relationships | FUTURE | NOT_IMPLEMENTED | 10,14,18 | No target configuration extraction [E10]. |
| BP-024 | Security identity/role/ownership graph | MVP | NOT_IMPLEMENTED | 10,14 | A function named for auth is not an extracted principal/resource/ownership relationship [E3,E4,E10]. |
| BP-025 | Sensitive asset classification with provenance | MVP | PARTIAL | 10,14,22 | Human policy marks protected operations; no DATA_ASSET classifier or public/internal/personal label model [E4,E10]. |
| BP-026 | Versioned trust zones and crossing relationships | MVP | NOT_IMPLEMENTED | 10,14,22 | No executable zone policy or transition extractor [E10]. |
| BP-027 | Typed context-appropriate security controls | MVP | PARTIAL | 10,13 | Named authorization declarations only; validation/sanitization/rate-limit/log/encryption effectiveness absent [E3,E4]. |
| BP-028 | Sources/sinks and relevant value binding | MVP | NOT_IMPLEMENTED | 10–14 | No source/sink/value-flow semantic model [E10]. |
| BP-029 | Observed/inferred/unknown control distinction | MVP | IMPLEMENTED | 10,12,14,28 | Supported declaration, unresolved/unsupported scope and external-policy caveats explicit; recognized does not mean effective [E3,E4]. |
| BP-030 | Stable normalized node IDs and edge types | MVP | IMPLEMENTED | 11,28 | Revision-scoped canonical hash IDs and validated graph references [E3,E4]. |
| BP-031 | Proposed graph vocabulary represented semantically | MVP | PARTIAL | 10–11 | Illustrative vocabulary is not an exact enum mandate; the substantive data/trust relations remain absent, not implied by schema allowance [E3,E4]. |
| BP-032 | File/range/analyzer/rule provenance | MVP | IMPLEMENTED | 11–12,28 | Evidence records preserve exact byte/range hashes and analyzer/query identity [E3,E4]. |
| BP-033 | Snapshot-specific reproducible graph persistence | MVP | IMPLEMENTED | 12,28 | JSON graph plus SQLite committed references; repeated source identity checked [E4,E7,E11]. |
| BP-034 | Raw analyzer outputs retained separately | MVP | PARTIAL | 12,16 | Normalized diagnostics/artifacts retained; no separate Joern/raw external analyzer output exists [E3,E7]. |
| BP-035 | Coverage exclusions/parse failures/unresolved constructs visible | MVP | IMPLEMENTED | 12,19,28 | Coverage records/diagnostics and viewer unknowns distinguish supported, skipped and unsupported [E3,E5]. |
| BP-036 | Sensitive endpoint-to-operation evidence path | MVP | IMPLEMENTED | 12–13,28–31 | Ordered HANDLES/CALLS path to human-policy protected function; source reachability only [E4,E11]. |
| BP-037 | R1 sensitive source-to-sink flow detector | MVP | NOT_IMPLEMENTED | 13–15,23,30 | LS-DATA-001 absent; needs actual value-flow and handling semantics [E10]. |
| BP-038 | R2 authorization relationship/coverage detector | MVP | PARTIAL | 14,23,30 | LS-AUTH-001 is declaration-context only; no object/tenant/ownership/effective policy proof [E4,E10]. |
| BP-039 | R3 trust-boundary handling detector | MVP | NOT_IMPLEMENTED | 14–15,23,30 | LS-TRUST-001 absent; crossing alone would not prove a weakness [E10]. |
| BP-040 | Define three rule specifications before prompts | MVP | IMPLEMENTED | 15,28 | Three documented rule contracts exist; two explicitly deferred, not executable support [E9]. |
| BP-041 | Rule prerequisites/controls/exceptions/blind spots/regressions | MVP | PARTIAL | 15 | AUTH subset has executable gating/tests; DATA/TRUST semantics and corpora remain research gates [E4,E9,E10]. |
| BP-042 | Deterministic graph paths and rule checks | MVP | IMPLEMENTED | 17,28 | NetworkX traversal and deterministic supported AUTH checks [E4]. |
| BP-043 | Candidate finding evidence/impact/unknowns/review advice | MVP | IMPLEMENTED | 13,19–20,28 | Finding model and report hold paths, impact hypothesis, caveats and review steps [E4,E5]. |
| BP-044 | Runtime evidence review can accept/reject/downgrade with reasons | MVP | PARTIAL | 16–17,28 | Deterministic graph/hash gate rejects malformed evidence; no semantic reviewer workflow or disposition history. Development security review is not this feature [E4,E10]. |
| BP-045 | Severity and confidence independent | MVP | IMPLEMENTED | 19–20,23,28 | Separate fields; candidates stay LOW confidence, no invented CVSS [E4,E5]. |
| BP-046 | Transparent multidimensional risk ranking | MVP | NOT_IMPLEMENTED | 16,23 | Findings deterministically ordered; no implemented impact/exposure/reachability/assets factor ranker [E4]. |
| BP-047 | LangGraph stateful parallel orchestration | TECH | SUPERSEDED | 15–17,23 | Approved linear Python pipeline for current delivery; LangGraph deferred pending measured need, not original blueprint fulfilled [E2,E9,E12]. |
| BP-048 | Repository Analyst role and structured manifest | MVP | PARTIAL | 16–17 | Intake/snapshot functions cover fixed manifest; broad language/eligibility understanding absent [E1,E2]. |
| BP-049 | Graph Analyst role/validated graph contract | MVP | IMPLEMENTED | 16–17 | Deterministic extraction and graph validation provide this bounded responsibility; separate LLM agent unnecessary [E3,E4]. |
| BP-050 | Architecture Analyst role/application facts | MVP | PARTIAL | 16 | Endpoint/dependency subset only, not databases/external configuration [E3]. |
| BP-051 | Security Analyst role/control/data/identity facts | MVP | PARTIAL | 16 | Declaration/protected-operation subset only [E3,E4]. |
| BP-052 | Threat Analyst role/schema-grounded hypotheses | MVP | PARTIAL | 16,21 | Bounded explanation schema and mock exist; no broader threat-taxonomy hypothesis engine [E6]. |
| BP-053 | Evidence Reviewer specialist role | MVP | NOT_IMPLEMENTED | 16–17 | No executable alternative-explanation adjudicator with accepted/rejected/downgraded results [E2,E4]. |
| BP-054 | Report Agent responsibility | MVP | IMPLEMENTED | 16 | Deterministic Markdown/JSON and validated optional explanation sidecars [E5,E6]. |
| BP-055 | Shared state including review results/security assets | MVP | PARTIAL | 17 | Snapshot/Graph/Finding/bundle contracts exist; complete proposed state/review history absent [E3,E6]. |
| BP-056 | Schema validate reasoning IDs/evidence and reject fabrications | MVP | IMPLEMENTED | 17,21 | Pydantic citation validation binds sidecars to exact bundle/finding IDs [E6]. |
| BP-057 | Minimal bounded model subgraphs and evidence | MVP | IMPLEMENTED | 8,17,21,29 | Redacted metadata/hash-only prompt context; whole repository not sent [E6]. |
| BP-058 | Workflow idempotence/resume without duplicates | MVP | PARTIAL | 17 | Stable IDs, locking and committed refs; no stateful resumable graph/role retry workflow [E2,E7]. |
| BP-059 | Record contradictions and alternative explanations | MVP | PARTIAL | 17 | Candidate caveats/unknowns and explanation fields; no cross-agent disagreement ledger [E4,E6]. |
| BP-060 | LLM sidecars cannot mutate canonical findings/graph; citations constrained | MVP | IMPLEMENTED | 17,20,29 | Immutable CANDIDATE/NEEDS_REVIEW facts; schema/citation rejection. Free-text prose remains UNREVIEWED and can invent unsupported assertions; semantic factuality is not established by valid citations [E4,E6]. |
| BP-061 | Meta adapter and provider provenance | MVP | PARTIAL | 8,20–21,23 | Bounded Standard-mode transport/mock, budget/provenance implemented; zero paid calls [E6,E10]. |
| BP-062 | Live Meta meaningful reasoning verified | MVP | BLOCKED | 8,23,25 | Account/privacy/access/owner authorization unresolved; mock is not live provider evidence [E10,E12]. |
| BP-063 | Core overview screen | MVP | PARTIAL | 19,28 | Fixed synthetic overview/status/counts/revision; no general database/service inventory [E5]. |
| BP-064 | Interactive graph/path navigation | MVP | IMPLEMENTED | 19,28 | Fixed bundled graph supports selection/path emphasis plus table fallback [E5]. |
| BP-065 | Filters by node type/risk/confidence/coverage | MVP | PARTIAL | 19,25 | Supported controls/path/table navigation do not implement every proposed filter dimension [E5]. |
| BP-066 | Finding details with evidence and uncertainty | MVP | IMPLEMENTED | 19–20,28 | Validated findings show evidence ranges/hashes, review steps and declaration limits [E5]. |
| BP-067 | Coverage/unknowns screen | MVP | IMPLEMENTED | 19,28 | Fixed viewer renders coverage/diagnostics and unsupported caveats [E5]. |
| BP-068 | Navigate finding to path to actual source lines | MVP | PARTIAL | 19,28–29 | Path plus file/range/hash metadata shown; source snippet/browser deliberately absent [E5,E9]. |
| BP-069 | Display analyzed commit and analysis version | MVP | PARTIAL | 19–20,29 | Content revision/schema/analyzer provenance displayed; target Git SHA/branch capture absent [E3,E5]. |
| BP-070 | Structured JSON and human-readable export | MVP | IMPLEMENTED | 16,20,29 | Verified bundle/graph/findings/coverage JSON and escaped Markdown report [E5,E7]. |
| BP-071 | HTML/PDF report export | TECH | SUPERSEDED | 16,20 | Approved Markdown plus fixed React viewer replaces optional format choice for delivered scope; no PDF export [E9]. |
| BP-072 | HTTP FastAPI backend service | TECH | SUPERSEDED | 20,30 | Approved CLI + fixed artifacts; no listener/API/upload endpoint [E2,E9]. |
| BP-073 | React/Vite visualization | TECH | IMPLEMENTED | 20,30 | React/TypeScript/Vite/Cytoscape fixed bundle viewer [E5]. |
| BP-074 | NetworkX graph integration | TECH | IMPLEMENTED | 3,20,30 | Local graph traversal, no dedicated graph DB [E4]. |
| BP-075 | SQLite/JSON persistence | TECH | IMPLEMENTED | 3,20,30 | Committed references and artifacts, validation and read-only inspector [E7]. |
| BP-076 | Modular analyzer-neutral adapter interface | MVP | IMPLEMENTED | 21 | CodeAnalyzer protocol separates graph contracts from AST extractor [E3]. |
| BP-077 | Resource-limited analysis worker | MVP | PARTIAL | 21,29 | Deadline/input/output caps and POSIX resource limits; Windows subset; not complete memory/process/sandbox enforcement [E8,E12]. |
| BP-078 | No target code/build/dependency execution | MVP | IMPLEMENTED | 21,29 | AST parsing only, no target imports; trusted project verification distinct from target execution [E1,E3,E8]. |
| BP-079 | Read-only OS mounts/filesystem and restricted network | MVP | BLOCKED | 21,29 | OS runner launch denied; no filesystem/network-denial probes passed [E10]. |
| BP-080 | Least privilege/separate worker boundaries | MVP | PARTIAL | 21 | Sanitized child environment and separated provider; no verified OS host isolation [E6,E8,E10]. |
| BP-081 | Secret prevention in model context/exported artifacts | MVP | IMPLEMENTED | 21,29 | Fixed synthetic manifest, hash/metadata exports and redaction tests; guarantee limited to supported profile [E1,E5,E6]. |
| BP-082 | Audit tool invocations/timeouts/policy decisions | MVP | PARTIAL | 21 | Scan/provider states and errors recorded; full sandbox policy audit unavailable [E2,E6,E7,E10]. |
| BP-083 | Controlled synthetic repository with known safe/weak/unknown cases | MVP | IMPLEMENTED | 18,23,28–30 | Separate fixture oracle and evaluation variants; intentionally narrow AUTH declaration ground truth [E11]. |
| BP-084 | Seeded recall/false-candidate measurement | MVP | PARTIAL | 18 | Measured declaration cases only; no three-detector vulnerability recall or production false-positive rate [E11]. |
| BP-085 | Path reconstruction/evidence completeness evaluation | MVP | IMPLEMENTED | 18 | Exact expected ordered paths/ranges/hashes and tamper checks for fixed corpus [E4,E11]. |
| BP-086 | Repository/endpoint/unknown coverage metrics | MVP | PARTIAL | 18 | Fixed denominators/unsupported constructs reported; no broad language/semantic completeness metric [E11]. |
| BP-087 | Analysis duration/repeatability measurement | MVP | IMPLEMENTED | 18 | Controlled run timing and repeated graph identity recorded [E11]. |
| BP-088 | Established tool vs context vs combined comparison | MVP | NOT_IMPLEMENTED | 18–19,23 | No Semgrep/CodeQL/Joern comparison or measured superiority/actionability study [E10,E11]. |
| BP-089 | End-to-end known-ground-truth candidate demonstration | MVP | IMPLEMENTED | 24,28–31 | Fixture intake → graph → AUTH candidate → verified export → viewer; narrower than full original MVP [E2,E5,E11]. |
| BP-090 | User/human review triage and feedback persistence | FUTURE | NOT_IMPLEMENTED | 24 | NEEDS_REVIEW enum is not reviewer workflow/history [E4,E10]. |
| BP-091 | Incremental Git updates and graph/commit comparison | FUTURE | NOT_IMPLEMENTED | 24 | Each scan snapshots fixture; no changed-node or history-diff engine [E2,E10]. |
| BP-092 | Dependency/advisory and secret scanners | FUTURE | NOT_IMPLEMENTED | 14,24 | Not target scanner integrations; project lock and redaction are different controls [E10]. |
| BP-093 | Additional frameworks/custom rule adapters | FUTURE | NOT_IMPLEMENTED | 24 | Only fixed FastAPI subset [E3,E10]. |
| BP-094 | CI/repository integration | FUTURE | PARTIAL | 24 | Native project CI and GitHub publication verified; no target-repository scanning integration [E12]. |
| BP-095 | C/C++ memory-safety pack | FUTURE | NOT_IMPLEMENTED | 14,24,27 | No bounds/lifetime/pointer analyzer [E10]. |
| BP-096 | JavaScript/TypeScript target analyzer | FUTURE | NOT_IMPLEMENTED | 24,27 | Frontend TypeScript does not mean target-language support [E10]. |
| BP-097 | IaC/cloud IAM graph | FUTURE | NOT_IMPLEMENTED | 24 | No provider/IAM policy extraction [E10]. |
| BP-098 | Authorized runtime evidence integration | FUTURE | NOT_IMPLEMENTED | 21,24 | No target runtime execution/telemetry [E10]. |
| BP-099 | Business-logic/abuse-case policy modeling | FUTURE | NOT_IMPLEMENTED | 24 | Protected-operation assertion is not full actor/resource/business rule analysis [E4,E10]. |
| BP-100 | Continuous/historical graph and advanced slicing | FUTURE | NOT_IMPLEMENTED | 24 | No update/history/slicing implementation [E10]. |
| BP-101 | Enterprise/multi-user collaboration/storage scale | FUTURE | NOT_IMPLEMENTED | 20,24 | Small local modular system; no distributed service [E10]. |
| BP-102 | Event eligibility/track/portal deliverable confirmation | EVENT | BLOCKED | 7–8,25 | Owner/portal gate; public event descriptions do not prove acceptance [E12]. |
| BP-103 | License and submission receipt | EVENT | BLOCKED | 25,32 | Source published; license choice and actual submission still pending [E12]. |
| BP-104 | Demo technical docs/screenshots/recording package | EVENT | PARTIAL | 25 | Docs/browser evidence exist; event-complete video/package/portal acceptance unverified [E5,E12]. |
| BP-105 | No complete-graph/exhaustive-security/novel-CPG claims | BOUNDARY | IMPLEMENTED | 4–7,22,26,29 | Maintained reports explicitly bound coverage, uncertainty and prior-art claims [E9,E10,E11]. |
| BP-106 | Autonomous exploitation/remediation/arbitrary network attacks | NON_GOAL | NOT_APPLICABLE | 4,21,29 | Explicitly excluded defensive product boundary; never planned as checklist feature [E9]. |
| BP-107 | Multiple initial scanners/distributed graph database | NON_GOAL | NOT_APPLICABLE | 6,20–21,25 | Optional later tool choices; no initial multi-engine or Neo4j obligation [E9,E10]. |

## Catalogue counts

| Status | All catalogue rows | Blueprint MVP behavior rows only |
|---|---:|---:|
| IMPLEMENTED | 37 | 33 |
| PARTIAL | 34 | 31 |
| NOT_IMPLEMENTED | 25 | 11 |
| BLOCKED | 6 | 3 |
| SUPERSEDED | 3 | 0 |
| NOT_APPLICABLE | 2 | 0 |
| **Total denominator** | **107** | **78** |

The MVP column excludes optional technology choices, event gates, future work and non-goals. It is a row inventory, not a delivery percentage. The original MVP remains incomplete because R1/R3 and semantic flow/control capabilities are absent, R2 is reduced, broader intake/isolation and live provider verification are blocked, and runtime semantic evidence review/ranking are incomplete.

## Complete Appendix B crosswalk

All **28 bullets** are mapped individually (B.1=5, B.2=6, B.3=7, B.4=5, B.5=5). Numbers below are audit ordinals within each printed subsection; they are not added PDF requirements. A bullet with multiple clauses can point to multiple atomic BP rows. Its completion is governed by the least-complete required clause, not by the strongest linked row.

| PDF bullet | Page | Paraphrased obligation | BP cross-reference |
|---|---:|---|---|
| B.1.1 | 28 | Confirm authorization/scope | BP-002 |
| B.1.2 | 28 | Capture URL/path, commit and branch | BP-003 |
| B.1.3 | 28 | Safe inventory and language/framework identification | BP-004 |
| B.1.4 | 28 | Exclusions and prompt/log secret redaction | BP-005 |
| B.1.5 | 28 | Persist configuration/tool versions | BP-006 |
| B.2.1 | 28 | Prove Joern representative parsing | BP-008 |
| B.2.2 | 28 | Modules/functions/calls/endpoints plus selected control/data flow | BP-010, BP-013, BP-014, BP-015, BP-017 |
| B.2.3 | 28 | Normalize IDs/types | BP-030 |
| B.2.4 | 28 | File/range/analyzer provenance | BP-032 |
| B.2.5 | 28 | Unresolved calls/unsupported files/parse failures | BP-035 |
| B.2.6 | 28 | Reproducible graph snapshot | BP-033; Git identity limit BP-003 |
| B.3.1 | 28 | Specify three rules before prompts | BP-040 |
| B.3.2 | 28 | Sources/sinks/assets/boundaries | BP-025, BP-026, BP-028 |
| B.3.3 | 28 | Three-valued control observations | BP-029 |
| B.3.4 | 28 | Graph paths/deterministic checks | BP-042 |
| B.3.5 | 28 | Candidates with evidence/unknowns | BP-043 |
| B.3.6 | 28 | Evidence review may reject/downgrade | BP-044, BP-053 |
| B.3.7 | 28 | Independent severity/confidence | BP-045 |
| B.4.1 | 28 | Overview/graph/findings/coverage screens | BP-063, BP-064, BP-066, BP-067 |
| B.4.2 | 29 | Finding → path → source lines | BP-068 |
| B.4.3 | 29 | Commit/analysis version shown | BP-069 |
| B.4.4 | 29 | Structured/human report export | BP-070 |
| B.4.5 | 29 | End-to-end known-ground-truth finding | BP-089 |
| B.5.1 | 29 | Resource-limited isolated worker | BP-077, BP-079 |
| B.5.2 | 29 | No default target execution | BP-078 |
| B.5.3 | 29 | Read-only source mounts/network restriction | BP-079 |
| B.5.4 | 29 | Necessary scoped model context | BP-057 |
| B.5.5 | 29 | Secret prevention in context/artifacts | BP-081 |

## Section and appendix coverage

The PDF reader map abbreviates the document, but the actual body contains **20 numbered sections**, not 18. Research/context passages are not automatically executable-feature obligations.

| PDF section | Pages | Audit treatment |
|---|---|---|
| 1 Executive summary | 2–3 | BP-001, BP-009, BP-036, BP-043; technology choices BP-047, BP-061, BP-073–075 |
| 2 Original concept/problem | 3–4 | Cross-layer scope BP-010–028; boundaries BP-105–107 |
| 3 Differentiation | 4–5 | Evidence/measurement BP-032–036, BP-083–089, BP-105; no demonstrated superiority claimed |
| 4 Research/prior art | 5–7 | BP-008–016, BP-088, BP-105, BP-107; CPG/OWASP/ASVS/NIST references are context, not certifications or mandatory scanner integrations |
| 5 Hackathon positioning | 7–8 | BP-057, BP-061–062, BP-102–104; historical schedule is not revalidated by this audit |
| 6 Three graph layers | 8–10 | BP-010–029 |
| 7 Schema/provenance | 10–12 | BP-030–035; vocabulary is illustrative, not a requirement to instantiate every enum or make FINDING a graph node |
| 8 Illustrative reasoning | 12–13 | BP-036, BP-038, BP-043, BP-045; example is not a real vulnerability claim |
| 9 Detection engines/rules | 13–15 | BP-016, BP-025–028, BP-037–041, BP-092, BP-095; six families described, three initial rules required |
| 10 Multi-agent workflow | 15–17 | BP-042–062; responsibilities may be deterministic functions; approved linear pipeline differs from proposed LangGraph |
| 11 Discovery/validation/tests | 17–19 | BP-077–089; development tests/review are not runtime evidence-review implementation |
| 12 Interface/report | 19–20 | BP-043–046, BP-063–070 |
| 13 Stack/integration | 20–21 | BP-047, BP-056–062, BP-070–076, BP-107; package/format choices distinguished from behavior |
| 14 Security boundaries | 21 | BP-001–007, BP-077–082, BP-098, BP-106 |
| 15 Feasibility critique | 22–23 | BP-025–029, BP-046, BP-088, BP-105; no complete-runtime-graph promise |
| 16 Risk prioritization | 23 | BP-043, BP-045–046; ordered findings are not a multidimensional risk model |
| 17 Roadmap | 23–24 | MVP rows across BP-002–089; later/research BP-090–101 |
| 18 Compressed delivery | 25 | BP-008, BP-037–047, BP-061–070, BP-083–089, BP-102–104; dated schedule not a current execution authorization |
| 19 Other idea comparison | 26 | Historical product-selection context; no obligation to build Zephyrus/CivicLens |
| 20 Technical verdict | 26 | BP-008–009, BP-047, BP-088, BP-105–107; feasibility judgment is not shipped implementation evidence |
| Appendix A choices | 27–28 | Python/FastAPI and controlled corpus chosen; hybrid ambition remains partial. Other languages/focuses are alternatives, not all MVP requirements |
| Appendix B checklist | 28–29 | Every bullet mapped individually above |
| Appendix C handoff | 29–31 | Repeats product, evidence, three rules/workflow and boundaries above; no duplicate counting for repeated requirements |
| Appendix D glossary | 31 | Definitions constrain interpretation: AST ≠ CFG/PDG/CPG, CALLS ≠ taint flow, severity ≠ confidence; not separate features |
| Reference register / closing note | 32–33 | Historical sources and bounded proof objective. No new source/API/event validation is claimed |

## What the implementation establishes

The foundation is concrete: a safe fixed synthetic manifest, reproducible deterministic graph, conservative declaration-context candidates, traceable evidence, verified exports, bounded optional explanations, fixed interactive viewer and successful native project CI. The proposed three-layer semantic graph remains sparse: actual packaged node kinds are MODULE/FUNCTION/API_ENDPOINT; typed metadata and policy assertions should not be advertised as a complete security graph. `graph.findings` is a valid separate finding representation; absence of a FINDING node is not itself a gap.

The next useful analysis increment is a predeclared controlled semantic capability experiment and review, as scoped in the [gated plan](02_NEXT_STAGE_PLAN.md). Existing controlled fixture experiments do not require opening arbitrary-repository intake. Broader intake specifically requires isolation proof first. Joern remains a candidate, LangGraph remains optional for a demonstrated orchestration need, and a public static website is a separate presentation option.
