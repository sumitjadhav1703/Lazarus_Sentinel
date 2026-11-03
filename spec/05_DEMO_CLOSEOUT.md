# Fixed-fixture demo closeout

The demo presents reproducible authorization-context evidence for a controlled synthetic FastAPI application. The [public competition viewer](https://sumitjadhav1703.github.io/Lazarus_Sentinel/) runs release revision `47c5d2ed4090ffa0d7b77c1882608a483bccfb26`, with native Windows, macOS and Ubuntu checks passing on PR #53. The earlier fresh-clone rehearsal used the PR #51 baseline.

A fresh clone on macOS arm64 passed all nine offline checks and returned the expected scan exit code 2. Initial dependency installation used the package registries because the local cache lacked a locked wheel. The new rehearsal command was verified separately in the closeout checkout.

## Rehearse from a fresh checkout

Use the locked setup in [the teammate guide](../docs/21_TEAM_HANDOFF.md). Then run these commands from the repository root.

```sh
uv run --project backend --locked --no-env-file python scripts/verify_demo.py
uv run --project backend --locked --no-env-file python scripts/prepare_demo.py --verify-only
npm run dev --prefix frontend
```

The verifier checks the shipped viewer and backend. The rehearsal creates a new controlled scan, invokes disabled and mock explanation modes, verifies annotation and graph binding, and exports a fresh bundle to the ignored artifact directory. It preserves the packaged viewer assets and budget ledger. Open the loopback URL printed by Vite to show the reviewed packaged demo.

## Three-minute walkthrough

1. **Evidence path.** Show the expected PARTIAL scan with 6 endpoints, 23 nodes, 36 relationships and 2 low-confidence candidates. Select GET /weak. Follow the handler and recorded calls to the protected operation. Open the source-location evidence.
2. **Control and uncertainty.** Select GET /protected and show the recorded authorization declaration. Open coverage and show the unsupported dynamic route registration. Explain that source declarations leave runtime enforcement unverified.
3. **Explanation.** Select GET /authenticated and expand the recorded live Meta explanation. Show its provenance and evidence links. The application validates citations and preserves the original finding.
4. **Reproduction.** Show the verifier result and fresh artifact identity. Give the teammate the release commit and ask them to repeat the locked setup on their machine. Record OS, tool versions, verifier output, expected scan exit 2, one screenshot, and any failure.

## Meta evidence review workflow

[Competition verification](06_COMPETITION_VERIFICATION.md) records the successful live run.

The demo orchestrator scans the fixed synthetic fixture, selects one low-confidence candidate, sends the selected evidence metadata to Standard Muse Spark 1.3, validates the response and its citations, and exports a verified bundle. The model supplies review assistance. The deterministic analyzer owns the graph and finding. The same command defaults to mock mode for offline rehearsal.

For an authorized and reviewed live run, load your local credential only in the backend process:

```sh
uv run --env-file .env --project backend --locked python scripts/prepare_demo.py --verify-only --provider meta
```

Keep the returned scan, annotation and bundle IDs. A successful live export reports `provider=meta`, `model=muse-spark-1.3`, and `generation=live`. The saved annotation is labeled `UNREVIEWED`. Check its narrative against the evidence before presenting it. A failed attempt produces a diagnostic and does not fall back to mock. Check the shared ledger before another authorized attempt.

To show the recorded annotation, build the viewer with `npm run build --prefix frontend -- --base /`. Copy the exported `bundle.json`, `graph.json`, and `explanations.json` from the returned artifact directory into `frontend/dist/demo/v1/`. Serve the ignored build locally:

```sh
uv run --project backend --locked --no-env-file python -m http.server 4173 --bind 127.0.0.1 --directory frontend/dist
```

Open `http://127.0.0.1:4173/`, choose the candidate identified by the annotation, and expand **Recorded live explanation**. Keep that build local until the generated narrative has passed publication review. The packaged viewer replays the independently reviewed live bundle. Offline rehearsal still exports mock bundles.

## External completion gates

- Second-person reproduction, real screen reader output, native 200% zoom, and audience feedback remain separate from local browser and CI results.
- A recorded live Meta annotation is available for the competition demo. Offline rehearsal defaults to mock and requires no credential.
- The current Pages deployment and Website link are verified. Any replacement still requires the publication review and URL smoke check.
- Owner verifies the actual portal requirements, records the license choice, and retains a submission receipt if submitting.

## Next AI increment after the freeze

The optional [LangGraph demo workflow](../docs/05_ORCHESTRATION.md) runs the existing scan, explanation and export stages. The next AI increment is resumable human review. Freeze checkpoint and replay behavior before enabling durable state. Checkpoint only safe identifiers and decisions, and prevent replay from repeating a paid request.

Production DATA and TRUST detectors and broader repository intake have their own evidence and isolation gates in [the semantic-stage plan](02_NEXT_STAGE_PLAN.md).
