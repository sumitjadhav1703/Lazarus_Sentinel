# Controlled value-provenance feasibility experiment

Date: 2026-11-03. Contract version: `semantic-spike/0.1.0`.

**Disposition: GO for this standalone research experiment only.** Owner explicitly approved a reviewed fallback for this increment. This contract is fallback-reviewed; it is not an Astra approval. Successful execution closes only the selected S01/S04 subset in [the next-stage plan](02_NEXT_STAGE_PLAN.md). Production DATA/TRUST rules, broader intake and runtime reachability remain unimplemented or unverified.

## Question and boundary

Can Python's already installed standard-library AST recover exact parameter-to-argument provenance through straight-line local assignments, distinguish overwritten values, and explicitly abstain outside a frozen syntax subset?

The experiment parses only a new, fixed synthetic corpus. It never imports, compiles or executes corpus code, resolves real callees, installs tools, contacts a provider or changes existing Graph/Finding contracts. `consume(...)` is a declared synthetic observation marker, not a recognized security sink. Parameter `source` is a declared provenance origin, not a claim of attacker control or sensitive data. No security policy, sanitizer effectiveness, exploitability, severity or vulnerability conclusion follows from any result.

## Frozen implementation interface and ownership

- Worker owns `scripts/semantic_spike.py`, `fixtures/semantic_spike/` and `backend/tests/test_semantic_spike.py` only. Coordinator owns integration/ledgers; reviewer owns this contract.
- Pure function: `analyze_source(source: bytes, *, file_path: str) -> dict`. Source is UTF-8 bytes. Return JSON-serializable results; no application imports required. Parser errors and unsupported constructs return explicit UNKNOWN diagnostics, never NO_FLOW.
- Script invocation: `uv run --project backend --locked python scripts/semantic_spike.py`. No arbitrary target/path argument. Read the fixed corpus and independently stored oracle; create a fresh UUID-named directory under ignored `artifacts/semantic-spike/` with `result.json`. Refuse to overwrite an existing run. Exit 0 only if all oracle checks and evidence validation pass; otherwise nonzero and retain the failed outcome.
- Do not edit production analysis, rules, schemas, CLI, original fixtures, generated historical reports, dependency locks or viewer assets.

## Exact supported subset

Each file contains exactly one undecorated synchronous function `case(source)` with one unannotated positional parameter, no defaults, positional-only/keyword-only parameters, variadics, return annotation or type parameters. No other module statements are accepted. Its nonempty body contains only:

1. `name = source`, `name = previously_bound_name`, or `name = literal`: exactly one plain Name target and a Name or scalar Constant expression. Accepted constants: string, int, float, bool and None. Reject assignment to `consume`; allow reassignment of `source` and other locals, replacing their current provenance.
2. Exactly one final expression statement `consume(value)`, with one positional Name or accepted Constant argument and no keywords. No other calls are permitted. `consume` is never defined, assigned or passed as a parameter in the subset.

Perform whole-file syntax validation before producing any conclusive flow outcome. Unknown names, tuple/chained/annotated/augmented assignments, attributes/subscripts, expression operators, imports, nested scopes, branching, loops, try/with/match, async/yield, decorators, returns, calls in values and extra statements are UNKNOWN for the whole file. Unrecognized syntax even after a marker must not be ignored. No `ast.walk` traversal may mistake a nested-scope assignment for a local sequential assignment.

Track each binding in statement order. A Name read copies its current origin/path. A literal creates a literal-origin path; subsequent assignments replace rather than union prior origins. Reassignment of `source` therefore kills its old parameter provenance for later reads, while previously copied values preserve their earlier origin. This is a single syntactic path under the stated model, not Python runtime behavior or all-path reasoning.

## Output and evidence

Per file return `status`, `reason`, `source_sha256`, `file_path` and `path`. Allowed statuses:

- `FLOW_OBSERVED`: marker argument derives from the original parameter binding in the supported subset.
- `NO_FLOW_IN_SUBSET`: marker argument derives from a literal in the supported subset. This is a negative control, never a safe-code classification.
- `UNKNOWN`: unsupported syntax, unresolved value, malformed source or a bound exceeded. Empty path plus explicit reason; include diagnostic location where available.

For either conclusive result, `path` contains ordered evidence entries for origin (parameter or literal assignment/marker literal), every relevant copy assignment and final marker argument. Record kind, start/end line, start/end column and SHA-256 of the exact UTF-8 AST source segment for each entry. Columns are AST UTF-8 byte offsets, not Unicode character offsets. Avoid duplicate entries when origin is the marker literal; specify and test that convention. Evidence must reconstruct against the same input bytes and have nonempty, in-range segments. No fabricated CALLS/FLOWS_TO edges or canonical Evidence/Finding records.

Top-level artifact records schema/analyzer version, Python version, script SHA-256, corpus/oracle byte hashes, current Git commit if available (otherwise explicitly unknown), fresh run ID, elapsed time, case outcomes and expected-versus-observed counts. Script and corpus hashes identify uncommitted work; Git commit alone is insufficient. No environment dump or source-secret discovery. Counts retain UNKNOWN in the total denominator; they are not accuracy estimates for real software.

## Frozen oracle: 12 development cases

Store synthetic `.py` files separately from `oracle.json`. The analyzer must not read expected outcomes; only the runner compares them. All snippets below are function bodies under `def case(source):`.

| ID | Body (semicolon denotes a new line) | Expected |
|---|---|---|
| P01 | `consume(source)` | FLOW_OBSERVED |
| P02 | `copy = source; consume(copy)` | FLOW_OBSERVED |
| P03 | `a = source; b = a; consume(b)` | FLOW_OBSERVED |
| P04 | `a = source; source = 'fixed'; consume(a)` | FLOW_OBSERVED |
| C01 | `consume('fixed')` | NO_FLOW_IN_SUBSET |
| C02 | `copy = source; copy = 'fixed'; consume(copy)` | NO_FLOW_IN_SUBSET |
| C03 | `source = 'fixed'; consume(source)` | NO_FLOW_IN_SUBSET |
| C04 | `a = 'fixed'; b = a; consume(b)` | NO_FLOW_IN_SUBSET |
| U01 | `copy = transform(source); consume(copy)` | UNKNOWN |
| U02 | `if source: copy = source; consume(source)` (proper indented branch) | UNKNOWN |
| U03 | `consume(missing)` | UNKNOWN |
| U04 | `consume(source); source = 'later'` | UNKNOWN |

Expected denominator: 12 files, 4 flow, 4 negative control, 4 unknown. Tests additionally cover invalid UTF-8/syntax, nested scope, rebinding `consume`, multi-target assignment, non-ASCII evidence, input cap, repeated-run determinism excluding run metadata, and parameter-copy preservation under reassignment. Independent reviewer adds at least one unseen supported overwrite/copy variant and one unseen excluded-syntax variant; record their actual outcomes separately, without claiming statistically independent generalization.

## Budget, verification and stop gates

No downloads or new dependencies. Use the existing Python 3.13 project environment. Fixed corpus maximum 16 files; per file 16 KiB and 256 AST nodes; aggregate source at most 256 KiB; artifact at most 1 MiB. Check bytes before parsing and catch decode/parse/recursion errors. Nodes are bounded after parse; this is not hostile-input isolation. Runner target elapsed budget 10 seconds and outer invocation timeout 30 seconds; no automatic retries on failure. A single local implementation/review tranche is sufficient; expand no grammar to make a failed case pass.

Run focused pytest plus Ruff on changed files and the existing backend suite to establish no production regression. Validate every emitted evidence segment independently in tests, including overwrite paths. Run the fixed experiment and preserve fresh output. Report local OS/Python and unrun native platforms explicitly; prior native CI does not verify this new script. Platform publication and second-person fresh-clone reproduction remain separate gates.

Reject completion if any expected UNKNOWN becomes a conclusive result, any path contains stale overwritten provenance, evidence cannot reconstruct, output overwrites an older run, code executes targets or a production detector claim is added. If a contract inconsistency is discovered, stop and revise this contract explicitly before changing expected results. A passing spike permits proposing the next semantic contract; it does not itself authorize S05 product integration.

## Review record

The owner approved the available coordinator and an independent reviewer as the fallback for this increment. Astra routing could not be verified. The worker implemented the frozen scope and the independent fallback reviewer accepted it after 11 focused tests and six additional in-memory cases covering overwrite behavior, excluded syntax, and Unicode and multiline evidence.

The fixed corpus matched 12 of 12 expected results on macOS arm64 with CPython 3.13.14. There were four observed flows, four literal-origin controls and four unknowns. The run completed within the outer 30-second limit. Its local artifact is `artifacts/semantic-spike/0be59eeb-9904-4b97-98a7-e4fb767b22e8/result.json`. Ruff lint and format, strict backend mypy, and the full backend suite passed (151 passed, one Windows-only skip). Native Windows and Linux execution of this increment remains unverified.

S01 and the selected standard-library AST S04 experiment are complete. The Joern feasibility track and S05 product integration retain separate gates.
