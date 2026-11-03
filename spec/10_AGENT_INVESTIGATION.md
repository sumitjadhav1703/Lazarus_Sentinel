# Agent investigation of one candidate

Written 2026-11-03. This increment is built and verified offline only. **No live call has been made.** The packaged public bundle in `frontend/public/demo/v1/` is unchanged.

## What it does

Muse Spark investigates one existing candidate by calling read-only tools over the committed graph. It ends by calling `submit_investigation`. The analyzer's finding stays authoritative. The output is a recorded, UNREVIEWED set of investigation notes and is never a verdict.

```sh
uv run --project backend --locked --no-env-file lazarus investigate --scan-id <scan_id> --finding-id <finding_id> --provider mock
uv run --project backend --locked --no-env-file lazarus demo export --scan-id <scan_id> --annotation-id <annotation_id> --investigation-id <investigation_id>
```

`--provider` defaults to `disabled`. `mock` runs a deterministic scripted investigation through the same loop, validation and export path, with no key and no ledger write.

## Contract

| Item | Rule |
|---|---|
| Tools | `get_finding`, `get_node`, `get_neighbors`, `get_evidence`, `list_endpoints`, `get_coverage`, and `submit_investigation` (final). Each tool is a pure lookup in `LoadedScan.graph`. There is no file, network or target access. |
| Data sent to Meta | IDs, names, types, declared properties, file paths, line ranges and excerpt hashes. **No source text.** The existing explanation egress policy applies unchanged. |
| Loop | At most 6 model calls (5 tool steps and 1 submit). `parallel_tool_calls: false`, `reasoning_effort: "low"`, `max_completion_tokens: 2048`. Each tool result is at most 6144 bytes. The request is at most 32768 bytes, and the mock run checks this limit too. |
| Rejected calls | These fail the run: an unknown tool, wrong argument names or types, non-JSON arguments, free text instead of a tool call, `finish_reason: length`, more than one call per turn, a turn limit with no submission, and an invalid submission. An unknown ID is returned to the model as a tool error and recorded. A third error fails the run. |
| Citations | `evidence_ids` must be evidence that a tool returned during this run **and** evidence of the finding. |
| Record | The record is `artifacts/investigations/<id>.json`, opened with exclusive create. It is bound to `scan_id`, revision, `graph_sha256`, and `request_sha256` (a hash of the prompt, tools, finding, provider and model). Each step stores the tool, arguments, status, result and result hash. |
| Replay | `validate_investigation` re-runs every recorded step against the graph and requires identical results. The bundle exporter and `scripts/verify_demo.py` apply it. The viewer checks bindings, step hashes and citations. |
| Budget | Live turns use a separate ledger, `artifacts/agent-budget.sqlite3`, capped at 20 calls and USD 1. The cap was approved by the owner on 2026-11-03. The shared `model-budget.sqlite3` explanation ledger (USD 3, five attempts) is never touched. Each call reserves at least USD 0.10 and settles from the reported usage. |
| Failure | The run fails closed. No partial trace is written, and calls are never retried. |
| Viewer | The **Agent investigation** panel appears under the recorded explanation only when the bundle lists `investigations.json`. Selecting a step highlights the node it inspected. A mock record is labelled "offline mock rehearsal". |

## Evidence (measured 2026-11-03 on branch `codex/agent-investigation`)

- `scripts/verify_demo.py` reported PASSED with `live_provider_attempts: 0` on the unchanged packaged bundle (6 endpoints, 23 nodes, 36 edges, 2 findings).
- Backend: 218 passed and 3 skipped. 32 of the passing tests are new investigation tests covering hostile model output, tampered records, request shape, a separate ledger and the attempt cap. The optional LangGraph tests passed (3). Frontend: 21 tests passed, and typecheck, lint and build passed.
- An end-to-end CLI rehearsal on a fresh scan recorded a 6-call mock investigation and exported a bundle with graph, explanation and investigation sidecars. The viewer rendered it on loopback. The record is about 7.9 KB, and the largest tool result was 1939 bytes.

## Not verified

- No live call has been made. It is not yet known whether `muse-spark-1.3` accepts these function tools with `parallel_tool_calls: false` and the reconstructed assistant message (`content: null` plus `tool_calls`). The first live run will show this.
- The viewer does not recompute `request_sha256` and does not replay tools. The backend verifier does both.

## Gates before a live run

1. Review by owner-approved Astra or an approved fallback reviewer. This change adds a tool-calling trust boundary and a new egress pattern.
2. Explicit owner authorization for one live investigation, with no silent retry.

## Packaging a live run (after both gates)

Run this in the checkout that holds the committed packaged scan `8f48abe7-df1b-44fa-b821-0bc3075c882f`. The candidate is GET /authenticated, finding `finding:sha256:0dafd0a6885d2fc6d1dbf06fa1cbf095f28b69577ae8a4d5879ae0843306d4a0`. The existing live annotation is `1c249ea1-6223-42e1-b926-3a7393f435e1`.

1. Run `lazarus investigate --scan-id 8f48abe7-df1b-44fa-b821-0bc3075c882f --finding-id <finding> --provider meta` with `MODEL_API_KEY` loaded.
2. Run `lazarus demo export --scan-id 8f48abe7-df1b-44fa-b821-0bc3075c882f --annotation-id 1c249ea1-6223-42e1-b926-3a7393f435e1 --investigation-id <new id>`.
3. Copy the four bundle files into `frontend/public/demo/v1/`. `git diff` must show `graph.json` and `explanations.json` byte-identical. Only `bundle.json` changes, and `investigations.json` is new.
4. Run `scripts/verify_demo.py`, then open a PR. The owner triggers the manual Pages deploy.
