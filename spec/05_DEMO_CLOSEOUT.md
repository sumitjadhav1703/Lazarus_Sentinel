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
3. **Explanation.** Return to the finding with the recorded mock annotation. Show its provenance and evidence links. Explain that the application validates citations and preserves the original finding. The demo uses the deterministic mock.
4. **Reproduction.** Show the verifier result and fresh artifact identity. Give the teammate the release commit and ask them to repeat the locked setup on their machine. Record OS, tool versions, verifier output, expected scan exit 2, one screenshot, and any failure.

## External completion gates

- Second-person reproduction, real screen reader output, native 200% zoom, and audience feedback remain separate from local browser and CI results.
- The Meta key authenticated previously. One settled request cost USD 0.007014 at ledger rates and did not produce a saved explanation. A new synthetic attempt requires the current provider review. Use the mock for offline rehearsal.
- Pages has a manual, opt-in workflow. Publication requires the release review and a successful URL smoke check before adding the repository Website.
- Owner verifies the actual portal requirements, records the license choice, and retains a submission receipt if submitting.

## Next AI increment after the freeze

Keep the existing scan, evidence validation, provider and persistence boundaries. Evaluate a small LangGraph pilot when there is a concrete need to pause for human review and resume. The candidate workflow is committed scan validation → evidence selection → one bounded provider attempt → annotation validation → human review → publication. Checkpoint only safe identifiers and decisions. Reuse the shared budget, and ensure replay cannot repeat transport after settlement or an unresolved reservation. Compare the pilot with the current linear workflow using offline tests before adding a runtime dependency.

Production DATA and TRUST detectors and broader repository intake have their own evidence and isolation gates in [the semantic-stage plan](02_NEXT_STAGE_PLAN.md).
