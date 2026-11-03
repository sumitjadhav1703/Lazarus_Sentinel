# 22 — Next phase: finite, gated team plan

Proposed execution order, updated 2026-11-02. Completed baseline/demo/viewer work must not restart. [Document 15](15_NEXT_STEPS.md) preserves N01–N18 dispositions; this plan turns remaining work into finite team assignments. [Document 23](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) records actual current checks and publication outcomes. P01 and P02 are now complete for the bounded fixed-fixture profile; document23 links native three-platform success and published main. Begin with P03, while P04/P06 can proceed independently. Other listed actions remain unexecuted proposals.

For product capability expansion, use the [original-blueprint audit and semantic-stage plan](../spec/README.md). Its S01 semantic contract can proceed alongside P03 reproduction and owner prerequisites; optional P10 website work does not close detector gaps. Existing P tasks remain valid and are not replaced by the audit.

| ID | Owner / dependency | Bounded task and acceptance gate |
|---|---|---|
| P01 | Coordinator + backend; first | Finish native Windows/macOS compatibility without weakening worker isolation, provider deadline, redaction or budget concurrency. Run locked offline verifier on native macOS and hosted Windows/macOS/Linux. Record exact commit, runner, counts and links; unsupported isolation stays explicit. |
| P02 | Coordinator; P01 checks | Publish the reviewed source to the owner-specified existing repository and branch; inspect existing remote history first, never force-push. Verify remote branch identity and hosted CI. Preserve owner PDF, secrets and generated evidence locally. License and default-branch choices remain explicit. |
| P03 | Teammate + coordinator; P02 | Reproduce from a fresh clone on a second machine with document 21. Verify expected PARTIAL scan and fixed viewer without credentials. Return platform/tool versions, all checks, one screenshot and exact blockers. Close only with recorded results; fix instructions rather than resetting old evidence. |
| P04 | UI teammate; independent of owner portals | Conduct one bounded feedback round across first-time users, developers and security reviewers. Test native 200% browser zoom and a real screen reader, keyboard selection, focus, 320px reflow, declaration/unknown wording and error states. Record browser/AT versions and observed issues; triage before any redesign. |
| P05 | UI teammate; measured need | Measure production cold load and graph render on the fixed 23-node graph. Existing roughly 839 kB chunk warning is not a benchmark. Consider lazy loading/code splitting only if measured latency or payload cost justifies it; preserve hash validation and accessible fallback. No arbitrary large-graph program in this task. |
| P06 | Owner; can run alongside P01–P05 | Resolve N01/N02/N13: portal eligibility, complete required deliverables, privacy/data-use mode, Meta account/model access and license. Do not reveal credentials. Record primary-source dates and owner decisions. No submission or paid request is implied. |
| P07 | Backend + Astra; P06 prerequisites | Only after explicit live-call authorization, recheck exact Meta protocol/model/prices and existing USD3/five-attempt shared ledger. Run one bounded synthetic explanation, no retry; retain immutable identities, usage/provenance and validated citations. Failed/ambiguous usage blocks further calls pending reconciliation. A successful call proves transport only, not security accuracy. |
| P08 | Security/Astra + infrastructure; before N15 | Resolve N14 with a reviewed runtime. Prove filesystem/network/credential denial, resource/deadline limits, cleanup and no host socket/agent exposure using controlled probes. A process limit or Windows Job Object is not filesystem/network sandbox evidence. Owner approves platform/runner before installation. Broader intake stays blocked until measured review passes. |
| P09 | Backend + research/Astra; P08 | Freeze one explicitly authorized, bounded next intake contract with provenance, caps, threat model, unknowns and predeclared fixture oracle. Implement only that contract. Joern spike remains optional/time-bounded; DATA/TRUST require real data-flow/policy evidence, never relabel CALLS. |

## Step-by-step execution rule

1. Coordinator selects one ready task, names its owner/files and freezes acceptance criteria. P06 owner work and P04 research can proceed independently.
2. Read current implementation and evidence; identify affected callers/tests/fixtures/config. Preserve backend-generated schema authority.
3. Make a scoped branch and smallest change. Use independent agents only within non-overlapping ownership boundaries.
4. Run relevant tests and integration checks; obtain Astra review for security-sensitive changes. Record unavailable checks as BLOCKED or NOT_RUN.
5. Update task board, decision register when necessary, and append AGENT.md session evidence. Close the P-item only after its acceptance gate is observed.

Keep the demo working throughout. No speculative API, LangGraph, microservices, upload UI, automatic remediation or global tool installation is required by this plan. A broader accuracy program, retention service and multi-language scanner remain separate future proposals.


## Optional next coding milestone: public demo readiness (P10, proposed)

The repository About description/topics are configured; Website remainsblank because no deployedURL exists. After selecting this increment, keep only the existing public synthetic viewer:

1. Preserve P03 teammate reproduction and run P04 accessibility/P05 loading measurements alongside development.
2. Make Vite assets and fixed bundle loading work under `/Lazarus_Sentinel/`, preserving the fixed artifact allowlist, hashes, schemas and invalid-data suppression. Test both local root and repository subpath; never add arbitrary URL/upload input.
3. Add production-preview and subpath regressions, then measure load/render before splitting Cytoscape or adding dependencies.
4. Prepare a reviewable GitHub Pages workflow and static-file inventory. Obtain required owner/Astra publication review before enabling deployment; source publication is not automatic deployment authorization.
5. Once selected deployment actually succeeds, verify the live synthetic graph/evidence, set the About Website to its realURL, and recheck the Deployments homepage option.

Acceptance: reviewed production build loads the same validated bundle at both supported bases, no secrets/backend/modelkeys are shipped, actual deployedURL works before being advertised. No release/package/deployment is created merely to populate sidebar counters. [Official Vite GitHub Pages guidance](https://vite.dev/guide/static-deploy.html#github-pages) documents the repository base-path requirement. This remains a proposal, not implemented or deployed work.


### P07 checkpoint — 2026-11-03

One owner-authorized Standard Muse Spark 1.3 call against a committed synthetic finding authenticated and returned billable usage. The ledger settled at USD 0.007014 estimated using the documented rates. Explanation recording failed with INTERNAL_ERROR after settlement. The exact response was discarded by the CLI error boundary, so the precise cause remains unknown. P07 is partial. An offline test now covers safe schema-rejection diagnostics. The next live check is a separate attempt under the existing budget and approval process.

[Meta pricing](https://dev.meta.ai/docs/pricing-rate-limits) · [Chat Completions protocol](https://dev.meta.ai/docs/protocols/chat-completions)

### Next-phase implementation checkpoint

- **P03 — awaiting teammate evidence.** Use the exact baseline PR revision and the credential-free steps in document 21 on a second machine. Return the commit, OS and tool versions, offline verifier summary, expected PARTIAL scan exit code, one viewer screenshot, and any failed command. A run on this workstation does not close the item.
- **P04 — partial.** Chrome 156 on macOS confirmed Tab reaches the skip link and Enter focuses main. At 320 px the page had no horizontal overflow. A corrupt graph response displayed the error alert and suppressed graph and summary. Native 200% zoom, a real screen reader and feedback across the three audiences remain open.
- **P05 — local baseline measured.** Five cache-disabled navigations in headless Chrome 156 at 1440×900 transferred a median 937,161 bytes over uncompressed loopback HTTP. Median workspace insertion was 44.5 ms. The second animation frame after graph canvas insertion was 73.0 ms median, used as a render proxy. The first navigation took 98.0 ms and 269.6 ms respectively. These measurements do not justify a code split for the fixed demo. Real-network latency was outside the test.
- **P07 — offline gate tested.** Stubbed transport exercises the actual CLI parser, validation, annotation and ledger paths. Known usage settles even on response rejection, and ambiguous usage prevents a second transport. Live verification remains open pending the required reviewer. The previous approval for a fallback reviewer covered the provenance experiment.
- **P08 — probe proposal, pending review.** Evaluate a disposable Linux VM on an owner-approved runner. Stage only synthetic inputs into read-only storage and give the worker an isolated writable output directory. Run without a host mount, forwarded sockets, credentials, or network interface. Probe denied reads and writes outside the designated paths, denied outbound DNS and TCP, missing environment and socket credentials, enforced CPU/memory/process/file limits, deadline and cancellation behavior, and cleanup after crash. Record runner/image identity, probe code, expected and observed outcomes, limits, and cleanup evidence. A critical reviewer must approve the runtime and the exact probes before setup. P09 stays blocked until all required probes pass.
- **P10 — locally ready for publication review.** The viewer resolves its fixed artifact paths from Vite's build base. Both production builds rendered in Playwright at their respective URLs. Corrupt graph responses produced an alert and no canvas at either base. The Pages workflow runs only on manual dispatch from main, with deployment opt-in disabled by default. Its inventory gate passed the clean build and refused a planted extra file. No Pages setting, deployment, or About URL has changed.
