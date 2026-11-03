"""Assess a fixed synthetic DATA policy and write a separate evidence report."""

import json
import sys
import uuid
from collections import Counter
from pathlib import Path

import semantic_spike as spike
from lazarus_sentinel.bundle import parse_json

OUTPUT_ROOT = spike.ROOT / "artifacts" / "data-assessments"
SCHEMA = "controlled-data-assessment/0.1.0"
SUPPORTED_POLICY = {
    "policy_version": "1",
    "rule_id": "LS-DATA-001",
    "scope": "fixture:semantic-spike",
    "source": {"selector": "case(source)", "classification": "synthetic-sensitive"},
    "sink": {"selector": "consume(value)", "classification": "synthetic-external"},
    "required_argument_origin": "literal",
}
OUTCOMES = {
    spike.FLOW: "CANDIDATE",
    spike.NEGATIVE: "NO_CANDIDATE_IN_SUBSET",
    spike.UNKNOWN: "NEEDS_CONTEXT",
}


def load_policy(data: bytes) -> dict:
    try:
        policy = parse_json(data)
    except (ValueError, RecursionError) as exc:
        raise spike.ExperimentError("INVALID_DATA_POLICY") from exc
    if policy != SUPPORTED_POLICY:
        raise spike.ExperimentError("UNSUPPORTED_DATA_POLICY")
    return policy


def validate_evidence(source: bytes, result: dict) -> None:
    try:
        if result["source_sha256"] != spike.digest(source):
            raise ValueError
        path = result["path"]
        status = result["status"]
        kinds = [entry["kind"] for entry in path]
        if status == spike.UNKNOWN:
            if path:
                raise ValueError
            return
        if status == spike.NEGATIVE and kinds == ["marker_literal"]:
            pass
        elif (
            len(kinds) < 2
            or kinds[0]
            != {spike.FLOW: "parameter", spike.NEGATIVE: "literal_assignment"}[status]
            or kinds[-1] != "marker_argument"
            or any(kind != "copy_assignment" for kind in kinds[1:-1])
        ):
            raise ValueError
        lines = spike.source_lines(source)
        previous_end = (0, 0)
        for entry in path:
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
        raise spike.ExperimentError("INVALID_DATA_EVIDENCE") from exc


def assess() -> Path:
    policy_bytes = spike.bounded_read(spike.CORPUS / "data_policy.json")
    policy = load_policy(policy_bytes)
    cases = {}
    for case in spike.CASE_IDS:
        path = spike.CORPUS / f"{case}.py"
        source = spike.bounded_read(path)
        observed = spike.analyze_source(
            source, file_path=path.relative_to(spike.ROOT).as_posix()
        )
        validate_evidence(source, observed)
        outcome = OUTCOMES[observed["status"]]
        cases[case] = {**observed, "outcome": outcome}
        if outcome == "CANDIDATE":
            cases[case]["confidence"] = "LOW"
    run_id = str(uuid.uuid4())
    report = {
        "schema": SCHEMA,
        "run_id": run_id,
        "policy": policy,
        "policy_sha256": spike.digest(policy_bytes),
        "analyzer": spike.VERSION,
        "analyzer_sha256": spike.digest(Path(spike.__file__).read_bytes()),
        "assessment_sha256": spike.digest(Path(__file__).read_bytes()),
        "counts": dict(Counter(case["outcome"] for case in cases.values())),
        "cases": cases,
        "limitations": [
            "Source and sink classifications are declared synthetic assumptions.",
            "Literal origin meets only this fixture policy.",
            "The report does not establish runtime data exposure or a vulnerability.",
        ],
    }
    data = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    if len(data) > spike.MAX_ARTIFACT:
        raise spike.ExperimentError("ARTIFACT_BYTES_EXCEEDED")
    run = OUTPUT_ROOT / run_id
    spike.reject_aliases(run)
    run.mkdir(parents=True, exist_ok=False)
    output = run / "result.json"
    # Write completely before making the result visible.
    pending = run / "result.tmp"
    with pending.open("xb") as stream:
        stream.write(data)
    pending.rename(output)
    return output


def main() -> int:
    if len(sys.argv) != 1:
        print("The fixed DATA assessment takes no arguments.", file=sys.stderr)
        return 2
    try:
        print(assess())
    except spike.ExperimentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError:
        print("DATA_ASSESSMENT_IO_FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
