# Submission freeze and next-phase cost plan

Updated 2026-11-03, IST. Release evidence is in [competition verification](06_COMPETITION_VERIFICATION.md). The [public demo](https://sumitjadhav1703.github.io/Lazarus_Sentinel/) replays the independently reviewed Muse Spark 1.3 result from deployment revision `47c5d2e`. The evidence graph and candidate come from deterministic analysis. The Meta workflow adds a cited explanation for review.

## Before midnight IST on November 3

| Priority | Action | Completion evidence |
|---|---|---|
| 1 | Open the public demo in a clean browser. Select **GET /authenticated** and expand **Recorded live explanation**. | Graph, policy context, coverage, provider identity and recorded prose render. No account or API key is needed to replay. |
| 2 | Prepare the entry using the public URL, repository, tested revision, screenshot or walkthrough recording, and scope summary below. | A teammate can open the links and reproduce the walkthrough from [the closeout guide](05_DEMO_CLOSEOUT.md). |
| 3 | Check the organizer portal for required fields, file formats, license terms and any live execution requirement. | The owner verifies the actual portal checklist. Store the submission receipt after submitting. |
| 4 | Freeze functionality. Fix only a broken submission link, demo regression, or requirement confirmed by the portal. | Preserve the last green deployment and keep the offline replay available. |

Suggested entry description: **Lazarus Sentinel is a graph-based security review assistant. On a controlled synthetic FastAPI fixture, it traces an authorization candidate to source evidence. Meta Muse Spark 1.3 explains that evidence, and the application validates the citations before exporting the annotation for human review.**

The public event page lists November 4 at 9:00 p.m. ET, which is November 5 at 07:30 IST. Midnight on November 3 is our internal code cutoff. Check the organizer portal for the deadline that applies to the entry. [Meta hackathon page](https://dev.meta.ai/events/global-hackathon).

## Cost controls

| Item | Observed or planned cost |
|---|---|
| Model usage to date | Four settled requests, **USD 0.023824 estimated** at ledger rates. The successful recording cost USD 0.004686 estimated. |
| Recorded browser replay and offline verification | **USD 0 in additional model calls.** Use the deployed recording and the mock rehearsal for repeated demos. |
| One remaining live attempt | The shared application ledger permits at most one further attempt under the existing five-attempt cap, subject to reconciliation and the USD 3 cap. The ledger reserves at least USD 0.10 before transport. A reservation is a budget hold. |
| Hosting | Keep the existing static deployment. This plan adds no paid backend, database, model service or runner. |
| After submission | Estimate any new workload from measured input and output tokens and an explicit request count before changing the cap. Include runner time and artifact storage separately. |

Current Standard Muse Spark 1.3 rates are USD 1.25 per million uncached input tokens and USD 4.25 per million output tokens. The model's reasoning tokens count toward output. Use a new paid request only if the portal actually requires live execution and the existing ledger allows it. [Meta pricing](https://dev.meta.ai/docs/pricing-rate-limits) · [Meta reasoning](https://dev.meta.ai/docs/reasoning).

## LangGraph integration

The earlier release used linear orchestration because the fixed flow had no pause or recovery requirement, and its live Meta result already passed validation. The opt-in LangGraph workflow now wraps the same stages. This keeps the submitted recording and default setup stable while making the agent workflow runnable for reviewers.

```sh
uv run --project backend --locked --extra langgraph --no-env-file python scripts/prepare_demo.py --verify-only --workflow langgraph
```

This command uses mock assistance and makes no model call. It creates a fresh verified bundle without replacing the public demo. The published Meta response came from the live linear flow. [Orchestration contract](../docs/05_ORCHESTRATION.md) · [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview).

## What we implement next

1. **Release evidence and usability.** Collect second-machine reproduction, native zoom and screen reader feedback, and fix observed blockers. Record the exact commit and commands.
2. **Resumable review, if needed.** Define the review decision and replay behavior first. A resumed session must reuse a validated annotation and must never repeat paid transport on replay. Store identifiers and review decisions only. Require crash, replay and budget regressions.
3. **Productize one detector at a time.** Start with the existing DATA assessment. Freeze the canonical value-path and policy contract, test positive/control/unknown and held-out variants, then wire it to the viewer. Apply the same process separately to TRUST and richer AUTH.
4. **Prove isolation before broader intake.** On a reviewed runner, measure filesystem, network, credential, resource and cleanup denials. Only then implement one authorized local-directory intake mode.
5. **Expand evaluation and integrations.** Track candidate/miss/false-alarm/unknown counts and evidence accuracy on a declared corpus. Scope Joern, SARIF, HTTP, and extra languages individually.

The competition release covers fixed synthetic analysis and a recorded Meta explanation. The full blueprint still includes canonical detector integration, broader input support, comparative evaluation, and runtime review workflows. [Next-stage plan](02_NEXT_STAGE_PLAN.md) · [Master checklist](03_MASTER_CHECKLIST.md).
