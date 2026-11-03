# Claude Code project entry point

@AGENTS.md
@docs/21_TEAM_HANDOFF.md

Read `AGENT.md`, `TASK_BOARD.md`, and the assigned task's contracts before changing code. `AGENT.md` is the living log; do not create a case-variant `Agent.md`.

Perform routine tasks only within the coordinator-assigned file boundary. Claude Code does not imply access to Codex Astra/Sol/Terra. Critical/security decisions require owner-approved Astra; if unavailable, stop that decision and request an approved fallback. Never fabricate model availability or silently substitute a Claude model for Astra.

Use the portable commands in document 21 and record measured checks, not historical counts. Preserve immutable artifacts, fixed synthetic scope and non-authoritative explanation wording. Do not read secret values, make paid calls, install global tools or widen intake.

## What this project is (snapshot 2026-11-03)

Lazarus Sentinel is a defensive, read-only, graph-first application-security analyzer. A finding is a **candidate for human review**, never a confirmed vulnerability.
- `CALLS` is not data flow, and `DEPENDS_ON` is not enforcement.
- Keep severity, confidence and coverage separate, and keep `unknown` explicit.

Repo: `sumitjadhav1703/Lazarus_Sentinel` (default branch `main`). License: **Apache-2.0** (`LICENSE`, `NOTICE`; owner decision D-031).

Implemented. Verify against `AGENT.md` and `TASK_BOARD.md`, which are the live ledgers:

- **Scan:** fixed `fixture:fastapi-demo` only (6 endpoints, 23 nodes, 36 edges, 2 LOW candidates). **PARTIAL / exit 2 is the expected result.**
  - Arbitrary repository intake, uploads and an HTTP analysis API are deferred.
  - No OS sandbox has been demonstrated.
  - Joern is NOT_ATTEMPTED.
- **Controlled assessments:** synthetic DATA, TRUST and actor/action/resource assessments (`scripts/assess_*.py`) with separate reports. They do not change the FastAPI graph contract.
- **Explanations:** disabled by default, plus an offline mock and a bounded Meta adapter. One live Muse Spark 1.3 annotation was validated and is replayed in the [public viewer](https://sumitjadhav1703.github.io/Lazarus_Sentinel/). The shared USD 3 / five-attempt ledger has four settled attempts (USD 0.023824 estimated).
- **Agent investigation** (`investigation.py`, `lazarus investigate`, [spec/10](spec/10_AGENT_INVESTIGATION.md)):
  - Muse Spark calls read-only graph tools and finishes with `submit_investigation`.
  - Every step is replayed on validation, and citations must have been returned by a tool.
  - It uses a separate agent ledger (`artifacts/agent-budget.sqlite3`, 20 calls / USD 1).
  - Built and tested offline. The live run needs review and owner authorization.
- **Weakness references** (`references.py`, `lazarus references`):
  - A static CWE-862 / OWASP A01:2025 mapping, mirrored in `frontend/src/rule-references.json`.
  - An optional Meta `web_search` refresh that keeps only allowlisted https citations, on the agent ledger.
  - Built and tested offline.
- **Optional extras** (not in the default install): `--extra langgraph` (opt-in LangGraph rehearsal over the same fixed stages, mock by default, no tracing).
- **Repository context for agents** (`context.py`, `context_index.py`, `context_mcp.py`, `frontend/src/AgentContext*`, [spec/09](spec/09_AGENT_CONTEXT.md)): `lazarus context build|query|serve --target self`, merged through PR #55. It is a structural index of this repository, not data flow or proof of behaviour. Optional extra: `--extra context-mcp`.

Never make a live provider call without the owner's explicit authorization in the current conversation.

## Commands (run from the repo root; same on macOS and Windows PowerShell)

```sh
uv sync --project backend --locked
npm ci --prefix frontend --ignore-scripts --no-audit --no-fund
uv run --project backend --locked python scripts/verify_demo.py        # full offline verifier
uv run --project backend --locked lazarus scan --target fixture:fastapi-demo
uv run --project backend --locked lazarus investigate --scan-id <SCAN> --finding-id <FINDING> --provider mock
uv run --project backend --locked lazarus references --rule-id LS-AUTH-001 --provider mock
uv run --project backend --locked pytest backend/tests
uv run --project backend --locked ruff check backend/src backend/tests
uv run --project backend --locked ruff format --check backend/src backend/tests
uv run --project backend --locked mypy --config-file backend/pyproject.toml backend/src
npm --prefix frontend run typecheck && npm --prefix frontend run lint && npm --prefix frontend test
npm run dev --prefix frontend                                          # viewer on loopback
```

- Add `--no-env-file` to `uv run` for anything that must not load `.env`.
- Optional-extra tests: `uv run --project backend --locked --extra langgraph --no-env-file pytest backend/tests/test_langgraph_demo.py` and `uv run --project backend --locked --extra context-mcp --no-env-file pytest backend/tests/test_context.py backend/tests/test_context_index.py`.
- Python is pinned to 3.13 (`backend/pyproject.toml`, `.python-version`), and Node to 24.14.0.
- Counts of passing tests change. Record the measured number from your own run, not a remembered one.

## Where things are

- **`backend/src/lazarus_sentinel/`**
  - `cli.py`, with commands `scan`, `demo export`, `explain`, `investigate`, `references` and `context build|query|serve`.
  - Repository context: `context.py`, `context_index.py`, `context_mcp.py`.
  - `models.py`: schema 0.1.0, authoritative.
  - Pipeline: `intake.py`, `worker.py`, `analysis.py`, `rules.py`, `service.py`.
  - Artifacts and reports: `persistence.py`, `bundle.py`, `report.py`.
  - `demo_models.py`: bundle and sidecar schemas.
  - Meta boundary: `explanations.py`, `investigation.py`, `references.py`, `meta_provider.py`, `budget.py`.
  - Tests are in `backend/tests/`.
- **`frontend/src/`:** the React 19 + Vite + Cytoscape viewer (`main.tsx`, `Investigation.tsx`, `validation.ts`) over the hash-verified static bundle in `frontend/public/demo/v1/`.
  - Do not edit packaged evidence by hand; `scripts/prepare_demo.py` creates new identities.
  - Optional sidecars: `explanations.json`, `investigations.json`, `references.json`.
- **`scripts/`:** trusted tools (`verify_demo.py`, `prepare_demo.py`, `inspect_artifacts.py`, `assess_*.py`, `semantic_spike.py`).
- **`fixtures/`:** synthetic targets. The expected-results oracle is test-only.
- **`docs/`:** numbered specs and evidence, 00-24. `docs/assets/` holds the README walkthrough GIF.
- **`spec/`:** blueprint audit, competition verification (06), submission (07), agent context (09), agent investigation (10).
- **Authority, newest first:** `AGENT.md` > `TASK_BOARD.md` > `spec/10_AGENT_INVESTIGATION.md` > `spec/06_COMPETITION_VERIFICATION.md` > `docs/24_CONTRIBUTOR_READINESS_AND_CI.md`.

## CI and GitHub workflow

- **`.github/workflows/ci.yml`** (name `CI`) runs only on pull requests and on pushes to `main`. Jobs:
  - `backend`: ruff, format check, mypy, pytest.
  - `frontend`: typecheck, lint, vitest, build.
  - `verify`: a 3-OS matrix (macOS, Windows, Ubuntu) that runs `scripts/verify_demo.py` plus the optional LangGraph and context-MCP tests.
- **Other workflows:** `codeql.yml` (Python and JS/TS, weekly) and `dependabot.yml`. `pages.yml` is a manual, opt-in static-viewer deploy from `main` with an output allowlist; do not trigger it.
- **Cancelled macOS job:** a hosted-runner queue cancellation is not a code failure. Re-run the job instead of editing code.
- **Issues:** the GitHub issue backlog (labels `good first issue`, `frontend`, `testing`, `ci`, `security`, `roadmap`, `owner-decision`) is the live task list for contributors. Check `gh issue list` for status.
- **Branches and PRs:** branch from current `main` (`codex/<task>` or `feat/<task>`), open a PR with the template, and wait for green checks. Never merge, push to `main`, trigger deploys or post to GitHub without the owner's explicit say-so in the current conversation.

## Hard rules for Claude Code in this repo

- Only edit files inside the file boundary the owner gave for the task. If told "read only" or "change only X", obey literally.
- Never read, print or commit `.env` values (check only whether a variable is set), the blueprint PDF, `artifacts/` contents, or secrets. `.env.example` is the only credential template.
- No paid or live provider calls, no target execution, no global installs, no widening of intake beyond the fixed fixture, no exploit payloads.
- Preserve immutable artifacts, historical reports and the published bundle bytes. Create new scan identities rather than rewriting old ones.
- Keep non-authoritative wording in UI and docs: "candidate", "unverified", "not data flow".
- Critical/security decisions (sandbox, intake, threat model, risk acceptance, new provider trust boundaries) need owner-approved Astra or an explicit owner-approved fallback. Claude cannot supply Astra.
- When a task finishes, append dated notes with measured results to `AGENT.md` and update `TASK_BOARD.md` through the coordinator. Decisions go in `docs/11_DECISIONS_AND_ASSUMPTIONS.md`.

These `@` imports follow [official Claude Code memory documentation](https://code.claude.com/docs/en/memory#import-additional-files), checked 2026-11-02. Verify loaded instructions with the installed client's supported context/memory inspection; model availability is separate from instruction loading.
