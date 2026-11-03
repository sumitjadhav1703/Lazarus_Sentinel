# Competition verification and controlled assessments

## Live Meta evidence assistant

The fixed-fixture workflow successfully recorded and exported a real Standard Muse Spark 1.3 explanation on 2026-11-03. It scans the synthetic fixture, selects a low-confidence authorization candidate, sends bounded evidence metadata, validates the response and its cited evidence IDs, and publishes an immutable annotation with the verified bundle. The graph and finding remain analyzer-owned.

- Scan: `8f48abe7-df1b-44fa-b821-0bc3075c882f`
- Annotation: `1c249ea1-6223-42e1-b926-3a7393f435e1`
- Bundle: `86700a21-649c-43da-bfc0-6253d5dfaa1d`
- Narrative review: independent owner-approved fallback reviewer confirmed the canonical GET /authenticated path and all five evidence IDs. The explanation preserves uncertainty about runtime enforcement and exploitability. The immutable annotation retains its original UNREVIEWED label.

The first two requests settled and returned no valid annotation. The explicit minimal reasoning setting reached JSON but failed local explanation validation. Strict provider-side JSON Schema, minimal reasoning and the existing local validation then produced the successful export. These were separately reviewed request changes, with no automatic retries. The successful request settled at USD 0.004686 estimated. The shared ledger records four settled attempts totaling USD 0.023824 estimated, with the existing USD 3 and five-attempt caps.

Chrome 156 replayed the live bundle on loopback, showing the exact narrative, model provenance and graph. The preview allowed only the fixed bundle assets and local application files. The screenshot is saved locally as `artifacts/release-closeout/viewer-meta-live.png`.

Use the [closeout guide](05_DEMO_CLOSEOUT.md) to replay the recorded result without another call. [Meta structured output](https://dev.meta.ai/docs/structured-output) · [Meta reasoning](https://dev.meta.ai/docs/reasoning) · [Meta pricing](https://dev.meta.ai/docs/pricing-rate-limits).

## Measured controlled assessments

Run from the repository root using the locked backend. Each command writes a new evidence report under ignored artifacts. Cases are fixed synthetic programs and their classifications are explicit policy assumptions.

| Assessment | Command | Measured outcomes |
|---|---|---|
| S05 value origin | `uv run --project backend --locked --no-env-file python scripts/assess_data.py` | 4 LOW candidates, 4 literal-origin controls, 4 NEEDS_CONTEXT |
| S06 zone handling | `uv run --project backend --locked --no-env-file python scripts/assess_trust.py` | 2 LOW candidates, 2 controls, 2 NEEDS_CONTEXT |
| S07 actor/action/resource | `uv run --project backend --locked --no-env-file python scripts/assess_auth_context.py` | 4 LOW candidates, 1 recognized declaration, 1 NEEDS_CONTEXT |

Each report binds the policy and source bytes and validates source spans. Unsupported constructs abstain. The measurements cover the declared synthetic subsets, with separate output formats from the fixed FastAPI scan. They establish neither production accuracy nor runtime control effectiveness. Canonical DATA/TRUST graph integration and a comparative S08 evaluation remain separate work.

## Remaining external and product gates

- Second-machine teammate reproduction, native assistive technology feedback, license choice, and the organizer's submission receipt require independent evidence.
- No approved isolation runner has passed the required filesystem, network, credential, resource and cleanup probes. Arbitrary repository intake remains disabled.
- LangGraph, Joern, additional languages and broader scanner integration remain research or product increments. The competition explanation uses the verified bounded Meta workflow.
