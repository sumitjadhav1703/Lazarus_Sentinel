# Fixed-fixture demo closeout

The demo presents reproducible authorization-context evidence for a controlled synthetic FastAPI application. Its release baseline is GitHub main at `ec7754dff49726b5a3283c994392f6239d315f0b`, which includes PR #51. The eight project checks passed on that PR, including native Windows, macOS, and Ubuntu verification.

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
- Pages has a manual, opt-in workflow. Publication requires the release review and a successful URL smoke check before adding the repository Website.
- Owner verifies the actual portal requirements, records the license choice, and retains a submission receipt if submitting.

## Next AI increment after the freeze

Keep the existing scan, evidence validation, provider and persistence boundaries. Evaluate a small LangGraph pilot when there is a concrete need to pause for human review and resume. The candidate workflow is committed scan validation → evidence selection → one bounded provider attempt → annotation validation → human review → publication. Checkpoint only safe identifiers and decisions. Reuse the shared budget, and ensure replay cannot repeat transport after settlement or an unresolved reservation. Compare the pilot with the current linear workflow using offline tests before adding a runtime dependency.

Production DATA and TRUST detectors and broader repository intake have their own evidence and isolation gates in [the semantic-stage plan](02_NEXT_STAGE_PLAN.md).
