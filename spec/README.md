# Lazarus Sentinel: blueprint audit and next-stage specification

Reviewed **2026-11-02** against the original **33-page, version 1.0 blueprint prepared 01 November 2026**, all numbered sections 1–20, appendices A–D and the closing note. This folder is a compact planning space for teammates using Claude Code or Codex.

For release rehearsal and remaining gates, see [demo closeout](05_DEMO_CLOSEOUT.md).

## Read in this order

1. [Implementation audit](01_BLUEPRINT_IMPLEMENTATION_AUDIT.md): source-page references, current evidence, implemented/partial/missing capabilities, approved substitutions and every Appendix B checklist item.
2. [Next-stage plan](02_NEXT_STAGE_PLAN.md): recommended execution order, owners, dependencies, acceptance tests and stop gates.
3. [Master checklist](03_MASTER_CHECKLIST.md): one status-tracked entry per audited capability. Check an item only after its stated scope is verified; partial or blocked is not done.

The audit below records the 2026-11-02 baseline. See the [first live API checkpoint](../docs/22_NEXT_PHASE_PLAN.md#p07-checkpoint--2026-11-03) and the [controlled value-provenance experiment](04_CONTROLLED_SEMANTIC_EXPERIMENT.md) for later work.

## Where the project actually stands

The approved reduced fixture/demo delivery works: bounded Python/FastAPI source parsing, deterministic structural graph, declaration-context authorization candidates, exact evidence, SQLite/JSON/Markdown outputs, immutable bundles, a fixed interactive viewer and native Windows/macOS/Linux checks. The shipped example has **6 endpoints, 23 nodes, 36 edges, 2 LOW-confidence candidates** and 3 recognized authorization declarations with effectiveness unverified.

The **original blueprint MVP remains incomplete**. Its three detector families are not three working detectors: R1 SensitiveDataFlow is absent; R2 AuthorizationCoverageGap has a narrower declaration-context implementation; R3 TrustBoundaryHandling is absent. No actor/resource ownership reasoning, usable value-flow engine, tested hostile-repository isolation, arbitrary authorized-repository intake, live Meta verification or runtime evidence-review/triage workflow is claimed.

An AST adapter, linear pipeline, CLI/static viewer and Markdown/JSON reports are approved current choices. Adding the names Joern, LangGraph or FastAPI HTTP to the stack would not itself close a semantic gap. Optional website work improves access to the existing demo; it does not implement missing analysis.

## Evidence and authority

- Audit checkpoint: repository `9f3d021581fe1a846fea418839ad84ee95e2fcd7`. Application source matches tested source commit `06f993e77237086ecf0f2abb40670082b6c84be0`; subsequent changes before this audit were documentation-only.
- Recorded verification: **139 backend passed / one Windows-only skip on the local Mac; 16 frontend passed**. Native Windows/macOS/Linux CI passed; see [release evidence](../docs/23_PORTABILITY_AND_RELEASE_VERIFICATION.md). These are recorded checks, not a new behavior-test run for this documentation task.
- Fresh read-only inspection confirmed the packaged graph contains 5 MODULE, 12 FUNCTION and 6 API_ENDPOINT nodes, with 36 structural/declaration edges. Graph type strings or planned schema vocabulary do not establish semantic extraction support.
- Original source: `Lazarus_Sentinel_Research_and_Implementation_Blueprint.pdf` in the repository root, SHA256 `894a76e0e24b467a8fb159238b4a2b29096ab9866881eaf41711e66cfe5c47fe`. The original is a confidential local input and remains untracked. This folder paraphrases requirements and cites PDF pages; it does not reproduce or publish the source PDF. Teammates without that local file can still follow the audit and public code references.
- [AGENTS.md](../AGENTS.md) governs safety and model routing. [Current log](../AGENT.md), [first-slice contract](../docs/13_FIRST_SLICE_CONTRACT.md), [demo contract](../docs/16_DEMO_DELIVERY_CONTRACT.md), [team handoff](../docs/21_TEAM_HANDOFF.md), [P01–P10 plan](../docs/22_NEXT_PHASE_PLAN.md) and [decision register](../docs/11_DECISIONS_AND_ASSUMPTIONS.md) remain authoritative for current implementation and accepted decisions.

Catalogue counts are **unweighted scope-item counts**, not percentages of engineering effort, detection coverage or product completion. Research references, future features and historical event tasks must not inflate a readiness claim.

## How to use this specification

Select one ready stage with the owner, freeze its evidence contract and file ownership, then implement and verify that increment. Unchecked tasks and this audit do **not** authorize new downloads, global tools, target execution, external model calls, deployment, broader intake or arbitrary remediation. Preserve old scans and use new identities. Record decisions and measured outcomes before changing checklist status.

Historical event dates, package releases, provider terms and tool prerequisites in the PDF are not freshly verified external facts. Recheck applicable primary sources and the owner's portal when a selected task depends on them.
