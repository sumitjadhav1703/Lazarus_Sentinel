"""Assess one explicit trust policy over fixed synthetic source markers."""

import ast
import json
import sys
from uuid import uuid4

import semantic_spike as spike
from lazarus_sentinel.bundle import parse_json

CORPUS = spike.ROOT / "fixtures" / "trust_assessment"
OUTPUT_ROOT = spike.ROOT / "artifacts" / "trust-assessments"
SCHEMA = "controlled-trust-assessment/0.1.0"
POLICY = {
    "policy_version": "1",
    "rule_id": "LS-TRUST-001",
    "scope": "fixture:trust-assessment",
    "entry": "transfer",
    "origin_zone": "internal",
    "destination_zones": ["internal", "partner"],
    "handoff_marker": "handoff",
    "required_handling": {"destination_zone": "partner", "marker": "check_consent"},
}
CASE_NAMES = ("candidate", "handled", "same_zone", "wrong_scope", "dynamic", "branch")
OUTCOMES = {"CANDIDATE", "NO_CANDIDATE_IN_SUBSET", "NEEDS_CONTEXT"}


def load_policy(data: bytes) -> dict:
    try:
        policy = parse_json(data)
    except (ValueError, RecursionError):
        raise spike.ExperimentError("INVALID_TRUST_POLICY") from None
    if policy != POLICY:
        raise spike.ExperimentError("UNSUPPORTED_TRUST_POLICY")
    return policy


def marker(statement: ast.stmt, name: str, zones: list[str]) -> str | None:
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return None
    call = statement.value
    if (
        not isinstance(call.func, ast.Name)
        or call.func.id != name
        or len(call.args) != 1
        or call.keywords
    ):
        return None
    arg = call.args[0]
    if (
        isinstance(arg, ast.Constant)
        and isinstance(arg.value, str)
        and arg.value in zones
    ):
        return arg.value
    return None


def assess_source(source: bytes, policy_bytes: bytes, *, file_path: str) -> dict:
    policy = load_policy(policy_bytes)
    result = {
        "file_path": file_path,
        "source_sha256": spike.digest(source),
        "policy_sha256": spike.digest(policy_bytes),
        "rule_id": policy["rule_id"],
        "policy_version": policy["policy_version"],
        "outcome": "NEEDS_CONTEXT",
        "transition": None,
        "evidence": [],
    }
    if len(source) > spike.MAX_SOURCE:
        return {**result, "reason": "SOURCE_BYTES_EXCEEDED"}
    try:
        module = ast.parse(source.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError, RecursionError):
        return {**result, "reason": "UNSUPPORTED_SOURCE"}
    if sum(1 for _ in ast.walk(module)) > 256:
        return {**result, "reason": "AST_NODES_EXCEEDED"}
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        return {**result, "reason": "UNSUPPORTED_ENTRY"}
    function = module.body[0]
    args = function.args
    if (
        function.name != policy["entry"]
        or function.decorator_list
        or function.returns is not None
        or function.type_params
        or args.posonlyargs
        or args.args
        or args.kwonlyargs
        or args.vararg
        or args.kwarg
        or len(function.body) not in (1, 2)
    ):
        return {**result, "reason": "UNSUPPORTED_ENTRY"}

    zones = policy["destination_zones"]
    handoff = function.body[-1]
    destination = marker(handoff, policy["handoff_marker"], zones)
    if destination is None:
        return {**result, "reason": "UNRESOLVED_HANDOFF"}
    handling = policy["required_handling"]
    control_zone = None
    if len(function.body) == 2:
        control_zone = marker(function.body[0], handling["marker"], zones)
        if control_zone is None:
            return {**result, "reason": "UNRESOLVED_HANDLING_SCOPE"}

    lines = spike.source_lines(source)

    def evidence(kind: str, node: ast.stmt) -> dict:
        location = {
            "kind": kind,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "start_col": node.col_offset,
            "end_col": node.end_col_offset,
        }
        return {**location, "sha256": spike.digest(spike.segment(lines, location))}

    observations = []
    if control_zone is not None:
        observations.append(evidence("handling_declaration", function.body[0]))
    observations.append(evidence("handoff_declaration", handoff))

    origin = policy["origin_zone"]
    if destination == origin:
        outcome, reason = "NO_CANDIDATE_IN_SUBSET", "SAME_ZONE"
    elif destination != handling["destination_zone"]:
        return {**result, "reason": "UNSPECIFIED_TRANSITION_POLICY"}
    elif control_zone == destination:
        outcome, reason = "NO_CANDIDATE_IN_SUBSET", "HANDLING_DECLARATION_PRESENT"
    else:
        outcome, reason = "CANDIDATE", "REQUIRED_HANDLING_DECLARATION_MISSING"
    return {
        **result,
        "outcome": outcome,
        "reason": reason,
        "transition": {"origin_zone": origin, "destination_zone": destination},
        "handling_destination_zone": control_zone,
        "evidence": observations,
    }


def main() -> int:
    if len(sys.argv) != 1:
        print("This assessment accepts no arguments.", file=sys.stderr)
        return 2
    try:
        policy_bytes = spike.bounded_read(CORPUS / "policy.json")
        policy = load_policy(policy_bytes)
        oracle_bytes = spike.bounded_read(CORPUS / "oracle.json")
        oracle = parse_json(oracle_bytes)
        if (
            not isinstance(oracle, dict)
            or oracle.keys() != set(CASE_NAMES)
            or any(
                type(outcome) is not str or outcome not in OUTCOMES
                for outcome in oracle.values()
            )
        ):
            raise spike.ExperimentError("INVALID_TRUST_ORACLE")
        results = {}
        for name in CASE_NAMES:
            path = CORPUS / f"{name}.py"
            results[name] = assess_source(
                spike.bounded_read(path),
                policy_bytes,
                file_path=path.relative_to(spike.ROOT).as_posix(),
            )
        mismatches = [
            name
            for name, result in results.items()
            if result["outcome"] != oracle[name]
        ]
        report = {
            "schema": SCHEMA,
            "policy": policy,
            "policy_sha256": spike.digest(policy_bytes),
            "oracle_sha256": spike.digest(oracle_bytes),
            "limits": "Synthetic declaration markers only. Runtime behavior is unverified.",
            "cases": results,
            "oracle_mismatches": mismatches,
        }
        encoded = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
        if len(encoded) > spike.MAX_ARTIFACT:
            raise spike.ExperimentError("ARTIFACT_BYTES_EXCEEDED")
        run_dir = OUTPUT_ROOT / str(uuid4())
        spike.reject_aliases(run_dir)
        run_dir.mkdir(parents=True, exist_ok=False)
        path = run_dir / "result.json"
        with path.open("xb") as stream:
            stream.write(encoded)
    except spike.ExperimentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, RecursionError):
        print("TRUST_ASSESSMENT_FAILED", file=sys.stderr)
        return 1
    print(path)
    return int(bool(mismatches))


if __name__ == "__main__":
    raise SystemExit(main())
