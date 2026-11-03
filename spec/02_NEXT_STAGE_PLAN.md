# Next stage: prove one additional security capability

Planning date: **2026-11-02**. This is a proposed gated sequence, not an implementation authorization. The [audit](01_BLUEPRINT_IMPLEMENTATION_AUDIT.md) explains the original blueprint gaps; the [master checklist](03_MASTER_CHECKLIST.md) tracks them. Preserve the completed reduced delivery and its evidence.

## Current disposition — 2026-11-03

The [competition checkpoint](06_COMPETITION_VERIFICATION.md) records the validated live Meta annotation and verified public Pages replay. The [controlled experiment](04_CONTROLLED_SEMANTIC_EXPERIMENT.md) completed S01 and the selected AST portion of S04. S05–S07 have executable, separate fixed-corpus assessments. Their measured results establish the supported synthetic cases. Canonical integration and the comparative S08 evaluation remain open. The Joern track remains setup-blocked.

For submission, rehearse the deployed recording using the [closeout guide](05_DEMO_CLOSEOUT.md). P03 second-machine evidence, P04 native accessibility feedback, and P06 portal/license decisions remain open. For the next engineering increment, run a scope-matched comparative evaluation and freeze a versioned evidence contract before adding DATA or TRUST paths to the viewer graph. S09 isolation must pass before S10 broader intake.

## Ordered work packages

| Stage | Owner and dependency | Concrete deliverable and acceptance | Stop condition |
|---|---|---|---|
| S01: freeze semantics | Coordinator + Astra; first | One written rule/capability subset with exact identities, supported syntax, evidence/path contract, impact assumptions, unknown behavior, positive/control/unknown oracle and bounded resources. Preserve existing AUTH findings and native setup. | Unresolved semantics, missing oracle or implicit security assumptions: do not code the detector. |
| S02: teammate reproduction | Teammate + QA; can run with S01 | Fresh clone on a second developer machine using document 21; record tool/OS versions, offline checks, expected PARTIAL scan and viewer screenshot. Resolve documentation/setup defects. | Hosted CI alone does not close a second-person reproduction task. Never reset historical evidence to hide a mismatch. |
| S03: external prerequisites | Owner; parallel | Record actual account access, required event deliverables, privacy/data-use choice and license decision. Verify current source dates and portal facts before commitments. | No credential disclosure, assumed eligibility, paid request or submission. |
| S04: analyzer feasibility | Sol compatibility + Astra; S01 and authorized setup | One time-bounded release-pinned Joern or selected alternative experiment on controlled synthetic source. Measure symbol/call/value-flow/source fidelity and unknowns against the oracle; retain raw output, versions, failures and a per-capability go/no-go. Recheck current runtime/platform/license prerequisites before setup. | Existing Joern outcome is SETUP_BLOCKED/analysis NOT_ATTEMPTED, not a failed Python capability measurement. Missing prerequisites remain blocked; no silent retries or global installation. |
| S05: one DATA subset | Sol backend + Astra; S04 demonstrated value semantics | Typed sources/sinks, actual value propagation, context-specific handling controls and policy/classification provenance for one case family. Implement positive/control/unknown outcomes, exact path evidence and a rule-specific validator. | Never rename CALLS to FLOWS_TO. A matching sanitizer name or source-to-sink path does not establish safe handling or exploitability. |
| S06: one TRUST subset | Sol backend + Astra; explicit boundary contract and sufficient extraction | One declared pair of zones, supported transition, expected handling and applicable controls. Version the policy and test positive/control/unknown cases. | A crossing or network call is not itself a weakness. No inferred trust zone from naming alone. DATA success does not automatically validate TRUST paths. |
| S07: richer AUTH subset | Sol backend + Astra; S01 and required semantic evidence | One actor/action/resource/policy relationship beyond dependency declarations. Specify supported ownership/tenant syntax, control scope and exceptions; test alternate paths, valid controls and unresolved behavior. | No runtime-enforcement claim from a declaration. Current shortest structural path is not an all-path authorization proof. |
| S08: evaluate correlation value | Independent QA + Astra; each selected rule | Small frozen corpus plus held-out variants; per-rule candidate/miss/false-alarm counts, path/source correctness, coverage/unknown denominator and timings. Compare one licensed, scope-matched analyzer only if selected. Show whether context changes interpretation. | No general accuracy, zero-false-positive or scanner-superiority claim from a tiny synthetic corpus. Do not require every scanner. |
| S09: prove OS isolation | Infrastructure + Astra; selected runtime, independent track | Controlled tests of filesystem/network/credential denial, read-only source access, resource limits, deadline/cancellation and crash cleanup. Record platform/policy and independently review. | Current worker/process limits and Windows locks are not a filesystem/network sandbox. Keep N14 BLOCKED until denial probes pass. |
| S10: one authorized intake mode | Sol backend + Astra; S09 passed | Freeze one allowlisted local-repository mode with explicit ownership, immutable byte identity, safe inventory, caps, unsupported language behavior and retention. Add archives only as a separate subsequent mode with traversal/link/device/decompression tests. | No broad upload service, arbitrary website/network scanning, target dependency installation or target execution. |
| S11: integrate and release | Sol integrator + Terra + independent QA/Astra; selected capability validated | Migrate schemas only where necessary; preserve old artifacts; expose actual new facts and unknowns in the viewer/report. Run native platform checks, P04 screen-reader/native 200% zoom and P05 loading measurements. Publish only a reviewed, reproducible selected scope. | Do not upgrade an enum, config file, research memo or model narrative into implemented capability. No automatic deployment or submission. |

The table preserves the original acceptance gates. S05/S06/S07 completed the separate synthetic assessment tier. Any canonical integration remains independently gated. S09 can proceed alongside controlled-fixture work. S10 starts after S09 acceptance.

## Next coding contract template

Before a worker edits code, fill these fields for exactly one selected stage:

```text
Task / audited BP IDs:
Owner / files owned / integration owner:
Existing interfaces and baseline to preserve:
Supported syntax and explicit exclusions:
Policy author/provenance and assumed impact:
Required node, edge, path and evidence semantics:
Positive case / valid-control case / unknown case:
Evaluation denominator and held-out variants:
Timeout, input/output/storage and setup budget:
Focused regression checks and native-platform gates:
Failure behavior / stop gate / rollback:
Independent reviewer and definition of done:
```

Record this contract in the selected task's specification. New flow/boundary paths need their own semantics and validation; the existing HANDLES/CALLS authorization validator must not silently accept them. Preserve graph 0.1.0 compatibility or explicitly version a reviewed migration. Keep model annotations separate from canonical findings.

## Conditional parallel lanes

### Live model explanation: P07

The recorded live explanation was validated, reviewed and replayed in Chrome. Use the published replay during judging. A future authorized live attempt must recheck the exact protocol/model/pricing and use the same USD 3/five-attempt ledger, deadline, citation validation and immutable recording. Ambiguous usage retains the reservation and blocks later calls.

### Website/distribution: P10

The reviewed static bundle is deployed, its public bytes were verified, and the repository Website points to it. Keep the static inventory restricted to the synthetic viewer and recorded bundle. Future deployments require the same publication review and URL verification.

### Workflow and analyst features

Add an evidence-review record with accepted/rejected/deferred outcomes only through a separate persistence/triage contract. Current CANDIDATE/NEEDS_REVIEW fields are defaults, not reviewer state transitions. Define transparent ranking factors before implementing a queue; do not multiply severity, confidence and coverage into an unexplained score.

The optional LangGraph demo wraps the fixed scan, explanation and export. Add durable review only after a concrete state or recovery need is measured. Use one read-only HTTP API only when fixed artifact loading is insufficient. Incremental/diff scans, reviewer feedback, SARIF, dependency/config/secrets integrations and additional frameworks each need separate finite contracts and tests.

## Later research and permanent boundaries

Keep JavaScript/TypeScript, C/C++ memory safety, IaC/IAM, authorized runtime telemetry, business-logic models, historical learning/prioritization and enterprise collaboration in individually scoped research tranches. A catalogue or tool's advertised language support is not implementation evidence.

Do not add automatic exploitation/remediation, unapproved active validation, universal vulnerability claims or a complete-runtime-graph promise. These are boundaries, not unchecked product features. Human reviewer and policy context remain essential.

## Completion rule

A stage closes only when its exact capability is implemented, meaningful tests and source evidence validate it, limitations are visible, native compatibility is checked, independent review is complete where required, and audit/checklist/log/task-board statuses agree. Report BLOCKED or NOT_IMPLEMENTED when a gate fails; do not spend the remaining schedule building a misleading substitute. The PDF's original dates and three-rule promise are historical context, not a newly validated delivery deadline.
