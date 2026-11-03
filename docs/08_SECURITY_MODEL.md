# 08 — Security, Privacy, Authorization and Isolation

> Team/platform update (2026-11-02): [team handoff](21_TEAM_HANDOFF.md), [finite next-phase plan](22_NEXT_PHASE_PLAN.md), and [current portability/publication evidence](23_PORTABILITY_AND_RELEASE_VERIFICATION.md) supersede earlier onboarding, remote-state and platform assumptions. Historical checks below retain their original date and scope.


## Integrated demo status — 2026-11-02

The approved [demo contract](16_DEMO_DELIVERY_CONTRACT.md) is implemented alongside the preserved first-slice analyzer: immutable hash-verified bundles, disabled/mock explanations with a gated Meta adapter, and a fixed React/Vite/TypeScript/Cytoscape viewer. See [capability gates](17_CAPABILITY_AND_RESEARCH_REPORT.md), [finite evaluation](18_DEMO_EVALUATION.md), and [integrated verification](19_INTEGRATED_DEMO_REVIEW.md) for current checks and review disposition. Document 14 remains historical first-slice evidence; its 73-test count is not the integrated total.

At this 2026-11-02 checkpoint, the recorded milestones were baseline `7797b85`, integrated demo `4f0346c`, and viewer refinement `2cda191`. The demo ran offline. The later [competition verification](../spec/06_COMPETITION_VERIFICATION.md) records the live Meta result, public Pages deployment, and separate controlled DATA, TRUST, and actor/action/resource reports. Fixed synthetic intake remains the supported scope.

## Current authorized boundary

The approved product scans only the checked-in synthetic `fixture:fastapi-demo`. It parses exact source bytes without importing/executing target code, installing target dependencies, probing services, exploiting findings or applying fixes. This is a controlled-fixture boundary; arbitrary repositories and archives are not accepted.

## Implemented protections

Manifest-driven fd-relative/no-follow reads reject invalid paths, symlinks and non-regular files. Limits are 100 Python files, 256 KiB per file, 5 MiB total source and 64 KiB each for manifest/policy metadata. Immutable snapshots retain exact bytes for parsing; evidence hashes and line ranges are validated, and source identity is rechecked before publication.

The extraction child uses a sanitized credential-free environment, 30-second coordinator deadline, 25-second CPU limit, 16 MiB output/file-size bound, 8 MiB input bound and 64-file-descriptor limit. Output locations are checked for existing symlink aliases; artifacts use generated scan directories. Public errors do not echo raw exceptions, host paths or source. Reports escape displayed metadata and retain locations/hashes rather than excerpts. The default provider is disabled; explicit mock is offline. The Meta adapter is present but live access is blocked; minimal synthetic context would leave the machine only under explicit live selection and the reviewed budget/privacy gates.

## Explicit limitations

Process/environment limits are not an OS filesystem/network sandbox. The worker can retain ambient OS access even though this pipeline does not intentionally perform network requests or execute targets. Do not claim enforced network isolation, read-only mounts, memory limits, containers or adversarial-repository readiness.

Existing-alias checks do not cover concurrent hostile filesystem replacement. Rename before SQLite commit can leave orphan files; readers use committed references only. Unknown-control suppression reduces false candidates but can miss real issues. Recognized declarations do not establish enforcement; no candidate is automatically confirmed.

## Future security gates — not implemented

Before broader authorized intake, review authorization/scope, read-only isolation, filesystem/network restrictions, credential access, output limits, hostile-input tests and cleanup/recovery. Archive support additionally needs member validation, expanded-size/file-count ceilings, link/device rejection and safe extraction. Container controls must be verified on the actual platform; containerization alone is insufficient.

Before any external model call, approve disclosed provider/model/egress, minimal relevant context, secret/personal-data redaction, no raw prompt logging, output schema/evidence-ID validation and a disabled/static alternative. Treat repository content and provider/tool output as untrusted data. No source instruction can override system/owner rules.

Future API/multi-user/triage work requires authentication, access control, tenant/scan ownership, retention/deletion and actor/rationale provenance. These are prerequisites for that expansion, not features already implemented. Never expose host credentials, SSH agent, Docker socket or broad host mounts to target analyzers.

## References for future design review

- OWASP threat modeling: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- OWASP API Security: https://owasp.org/www-project-api-security/
- NIST SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- Docker isolation references: https://docs.docker.com/engine/security/

These references are guidance, not certification of the current implementation.

## Bounded cross-platform compatibility contract — 2026-11-02

The portability increment preserves POSIX directory-relative/no-follow reads and POSIX resource controls. The approved Windows design rejects reparse/junction ancestry, non-exact path case, reserved names and nonregular or unstable files; it retains byte caps and parent deadlines. CPU/file-descriptor resource limits are POSIX-specific; Windows compatibility does not establish equivalent OS resource or filesystem/network isolation. Meta child startup uses the platform-supported process context without changing redaction, budget or absolute-deadline requirements. See document 23 for measured implementation/native-run outcomes. N14 denial probes remain required before broader intake.

## Agent investigation and web-search references — 2026-11-03

**New trust boundaries.** Both are added beside the existing explanation adapter:
- a tool-calling turn on `/v1/chat/completions`
- a Responses call with Meta's built-in `web_search` on `/v1/responses`

**Egress:**
- Investigations send graph metadata only: IDs, names, types, declared properties, paths, line ranges and hashes. They never send source text.
- Web search sends one fixed per-rule question, with no code, graph or finding text.

**Controls:**
- Exact request-shape allowlists.
- One tool call per turn.
- Strict argument validation, with unknown tools rejected.
- Result size caps.
- Citations restricted to tool-returned evidence of the finding.
- Web citations restricted to https on `cwe.mitre.org` and `owasp.org`.
- A separate fail-closed ledger: 20 calls and USD 1, with web-search fees settled at USD 2.50 per 1,000 queries.
- No retries.
- Every recorded tool step is replayed on validation.

**Status.** These boundaries are implemented and tested offline. Before any live call, they need review by Astra or an owner-approved fallback reviewer, plus explicit owner authorization ([spec/10](../spec/10_AGENT_INVESTIGATION.md)).
