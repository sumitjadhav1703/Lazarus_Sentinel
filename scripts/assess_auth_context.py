"""Assess actor, action and resource declarations in a fixed synthetic corpus."""

import ast
import json
import sys
import uuid
from collections import Counter
from pathlib import Path

import semantic_spike as spike
from lazarus_sentinel.bundle import parse_json

CORPUS = spike.ROOT / "fixtures" / "auth_context_assessment"
OUTPUT_ROOT = spike.ROOT / "artifacts" / "auth-context-assessments"
CASES = (
    "missing",
    "wrong_actor",
    "wrong_action",
    "wrong_resource",
    "recognized",
    "dynamic",
)
SCHEMA = "controlled-auth-context-assessment/0.1.0"
POLICY = {
    "policy_version": "1",
    "scope": "fixture:auth-context-assessment",
    "rule_id": "LS-AUTH-CONTEXT-001",
    "actor_parameter": "actor",
    "resource_parameter": "resource",
    "action": "export",
    "protected_sink": "export",
    "authorization_marker": "authorize",
}


def load_policy(raw: bytes) -> dict:
    try:
        policy = parse_json(raw)
    except (ValueError, RecursionError) as exc:
        raise spike.ExperimentError("INVALID_AUTH_CONTEXT_POLICY") from exc
    if policy != POLICY:
        raise spike.ExperimentError("UNSUPPORTED_AUTH_CONTEXT_POLICY")
    return policy


def call_args(stmt: ast.stmt, name: str, arity: int) -> list[ast.expr] | None:
    call = stmt.value if isinstance(stmt, ast.Expr) else None
    if (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == name
        and not call.keywords
        and len(call.args) == arity
    ):
        return call.args
    return None


def validate_evidence(source: bytes, evidence: list[dict]) -> None:
    try:
        lines = spike.source_lines(source)
        previous_end = (0, 0)
        for entry in evidence:
            start = (entry["start_line"], entry["start_col"])
            end = (entry["end_line"], entry["end_col"])
            if (
                start < previous_end
                or end <= start
                or spike.digest(spike.segment(lines, entry)) != entry["sha256"]
            ):
                raise ValueError
            previous_end = end
    except (KeyError, TypeError, ValueError) as exc:
        raise spike.ExperimentError("INVALID_AUTH_CONTEXT_EVIDENCE") from exc


def analyze(source: bytes, file_path: str, policy: dict) -> dict:
    result = {"file_path": file_path, "source_sha256": spike.digest(source)}
    unknown = {**result, "outcome": "NEEDS_CONTEXT", "evidence": []}
    if len(source) > spike.MAX_SOURCE:
        return {**unknown, "reason": "SOURCE_BYTES_EXCEEDED"}
    try:
        module = ast.parse(source.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError, RecursionError):
        return {**unknown, "reason": "UNSUPPORTED_SOURCE"}
    if sum(1 for _ in ast.walk(module)) > 256:
        return {**unknown, "reason": "AST_NODES_EXCEEDED"}
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        return {**unknown, "reason": "UNSUPPORTED_MODULE"}
    function = module.body[0]
    args = function.args
    actor = policy["actor_parameter"]
    resource = policy["resource_parameter"]
    if (
        function.name != "case"
        or function.decorator_list
        or function.returns is not None
        or function.type_params
        or args.posonlyargs
        or args.kwonlyargs
        or args.vararg
        or args.kwarg
        or args.defaults
        or [arg.arg for arg in args.args] != [actor, resource]
        or any(arg.annotation is not None for arg in args.args)
        or len(function.body) not in {1, 2}
    ):
        return {**unknown, "reason": "UNSUPPORTED_CASE"}
    sink = function.body[-1]
    sink_args = call_args(sink, policy["protected_sink"], 1)
    if (
        not sink_args
        or not isinstance(sink_args[0], ast.Name)
        or sink_args[0].id != resource
    ):
        return {**unknown, "reason": "UNRESOLVED_RESOURCE"}
    spans: list[tuple[str, ast.AST]] = [
        ("actor_parameter", args.args[0]),
        ("resource_parameter", args.args[1]),
    ]
    mismatches = []
    if len(function.body) == 2:
        check = function.body[0]
        check_args = call_args(check, policy["authorization_marker"], 3)
        if check_args is None:
            return {**unknown, "reason": "UNRESOLVED_AUTHORIZATION"}
        subject, action, target = check_args
        if (
            not isinstance(subject, ast.Name)
            or subject.id not in {actor, resource}
            or not isinstance(action, ast.Constant)
            or type(action.value) is not str
            or not isinstance(target, ast.Name)
            or target.id not in {actor, resource}
        ):
            return {**unknown, "reason": "UNRESOLVED_AUTHORIZATION"}
        if subject.id != actor:
            mismatches.append("ACTOR_MISMATCH")
        if action.value != policy["action"]:
            mismatches.append("ACTION_MISMATCH")
        if target.id != resource:
            mismatches.append("RESOURCE_MISMATCH")
        spans.append(("authorization_declaration", check))
    else:
        mismatches.append("DECLARATION_MISSING")
    spans.append(("protected_operation", sink))
    lines = spike.source_lines(source)
    evidence = []
    for kind, node in spans:
        entry = {
            "kind": kind,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "start_col": node.col_offset,
            "end_col": node.end_col_offset,
        }
        evidence.append({**entry, "sha256": spike.digest(spike.segment(lines, entry))})
    result.update(
        outcome="CANDIDATE" if mismatches else "DECLARATION_RECOGNIZED",
        diagnostics=mismatches,
        evidence=evidence,
    )
    if mismatches:
        result["confidence"] = "LOW"
    return result


def assess() -> Path:
    raw = spike.bounded_read(CORPUS / "policy.json")
    policy = load_policy(raw)
    cases = {}
    for case in CASES:
        path = CORPUS / f"{case}.py"
        source = spike.bounded_read(path)
        result = analyze(source, path.relative_to(spike.ROOT).as_posix(), policy)
        validate_evidence(source, result["evidence"])
        cases[case] = result
    run_id = str(uuid.uuid4())
    report = {
        "schema": SCHEMA,
        "run_id": run_id,
        "policy": policy,
        "policy_sha256": spike.digest(raw),
        "analyzer_sha256": spike.digest(Path(__file__).read_bytes()),
        "evidence_helper_sha256": spike.digest(Path(spike.__file__).read_bytes()),
        "counts": dict(Counter(case["outcome"] for case in cases.values())),
        "cases": cases,
        "limitations": [
            "Synthetic declarations and parameter identities are policy assumptions.",
            "Matching declarations leave runtime enforcement unverified.",
            "A candidate does not establish that runtime actors or resources differ.",
        ],
    }
    data = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    if len(data) > spike.MAX_ARTIFACT:
        raise spike.ExperimentError("ARTIFACT_BYTES_EXCEEDED")
    run = OUTPUT_ROOT / run_id
    spike.reject_aliases(run)
    run.mkdir(parents=True, exist_ok=False)
    output = run / "result.json"
    pending = run / "result.tmp"
    with pending.open("xb") as stream:
        stream.write(data)
    pending.rename(output)
    return output


def main() -> int:
    if len(sys.argv) != 1:
        print(
            "The fixed authorization context assessment takes no arguments.",
            file=sys.stderr,
        )
        return 2
    try:
        print(assess())
    except spike.ExperimentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError:
        print("AUTH_CONTEXT_ASSESSMENT_IO_FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
