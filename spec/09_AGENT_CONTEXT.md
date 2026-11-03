# Repository context for agents

The repository context graph is a local, read-only structural index of Lazarus Sentinel itself. The FastAPI security graph, findings, and published recording use their existing contract.

## Build, query, and serve

Install locked backend and frontend dependencies first. The TypeScript adapter loads the pinned compiler and parses source text. It never runs a target module.

```sh
uv run --project backend --locked --no-env-file lazarus context build --target self
uv run --project backend --locked --no-env-file lazarus context query --snapshot <UUID> --operation search --text validate_graph
uv run --project backend --locked --no-env-file lazarus context query --snapshot <UUID> --operation entity --id <ENTITY_ID>
uv run --project backend --locked --extra context-mcp --no-env-file lazarus context serve --snapshot <UUID>
```

The optional MCP stdio server exposes one read-only tool, `repository_context`. Inputs are `operation`, optional `entity_id`, `text`, and `cursor`. Only search takes text. Entity, neighbors, and evidence require an exact ID. Overview takes neither. Repeat the same query with the returned cursor for the next page. Results are capped at 100 records and 64 KiB. The server pins an already verified snapshot for its lifetime. It does not build, change, or expose snapshots over HTTP.

The ignored `artifacts/context/<UUID>/` directory contains `manifest.json`, `graph.json`, and `schema.json`. The manifest records SHA-256 and size for the graph and schema, graph digest as the context revision, and the separately captured Git HEAD. Indexed file hashes describe the working-tree bytes captured from tracked paths. They may differ from HEAD on a dirty checkout. The fixed allowlist covers backend Python, trusted Python utilities, frontend TypeScript/TSX, and selected package and parser configuration. Symlinks and unsupported paths fail closed. The export contains structural names and source coordinates with file hashes. It omits raw source excerpts and model output.

The local **Agent Context** panel accepts manifest and graph files, verifies size, hashes and references, and lets a human inspect or copy the entity response used by the agent. It does not upload files. Checksums detect corruption. Establish the bundle's origin separately before trusting externally supplied facts.

## Coverage and validation

Observed calls are limited to the supported syntactic resolution subset. Unresolved, dynamic, or ambiguous constructs are reported separately. This index does not establish runtime execution, data flow, authorization effectiveness, or complete codebase understanding.

Run the offline source-anchor evaluation after building the approved self snapshot:

```sh
uv run --project backend --locked --no-env-file python scripts/evaluate_context.py --snapshot <UUID>
```

The frozen questions cover CLI dispatch, scanner orchestration, graph validation, budget reservation, and viewer loading. This compares deterministic retrieval against file paths, with exact definition starts and context byte counts. It is not a model reasoning benchmark.

## Release gates

The implementation and temporary-repository tests are local. Complete the required security review before release of the real self-index and MCP boundary. Native CI, real-repository evaluation, broader intake isolation, and canonical DATA/TRUST/AUTH integration remain separate checks. The hosted security demo uses the original artifacts.

### Measured self-index release evidence

The owner authorized the release and independent fallback review. The reviewer found a missing budget anchor line in the frozen answer key, which was corrected before evaluation. Two local builds over identical tracked working-tree bytes produced identical graph and schema hashes. The graph captured 45 files, 315 entities, 667 relationships, 123 coverage records, and 2,050 explicit unknowns.

All five expected definition starts matched. The path-only baseline found five files and zero definition spans, using 195 response bytes. The structured queries used 12,032 bytes in total and returned zero unsupported claims in this five-question test. The questions include file hints, so this establishes source-anchor retrieval for the named cases. It does not measure general agent reasoning.

Snapshot `39ae0bd4-0add-4b55-a66e-e41a63a7632d`, graph revision `efc39a3ea2a327f6eb36de2b610f645b2a968b596420851125ddaec07cedc5c2`. The local export remains outside Git.
