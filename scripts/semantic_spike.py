"""Run the fixed, AST-only synthetic value provenance experiment."""

import ast
import hashlib
import json
import platform
import re
import stat
import subprocess
import sys
import time
import uuid
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "fixtures" / "semantic_spike"
OUTPUT_ROOT = ROOT / "artifacts" / "semantic-spike"
VERSION = "semantic-spike/0.1.0"
MAX_SOURCE = 16 * 1024
MAX_ARTIFACT = 1024 * 1024
FLOW, NEGATIVE, UNKNOWN = "FLOW_OBSERVED", "NO_FLOW_IN_SUBSET", "UNKNOWN"
CASE_IDS = tuple(f"{group}{index:02}" for group in "PCU" for index in range(1, 5))


class ExperimentError(ValueError):
    """A fixed diagnostic code safe to record in an artifact."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_lines(source):
    return re.split(rb"(?<=\n)|(?<=\r)(?!\n)", source)


def segment(lines, entry):
    start, end = entry["start_line"] - 1, entry["end_line"] - 1
    left, right = entry["start_col"], entry["end_col"]
    if not (0 <= start <= end < len(lines)):
        raise ExperimentError("EVIDENCE_LINE_OUT_OF_RANGE")
    if not (0 <= left < len(lines[start]) and 0 < right <= len(lines[end])):
        raise ExperimentError("EVIDENCE_COLUMN_OUT_OF_RANGE")
    data = b"".join(lines[start : end + 1])[
        left : sum(map(len, lines[start:end])) + right
    ]
    if not data:
        raise ExperimentError("EMPTY_EVIDENCE")
    return data


def analyze_source(source: bytes, *, file_path: str) -> dict:
    result = {"source_sha256": digest(source), "file_path": file_path}

    def unknown(reason, node=None):
        location = {}
        if getattr(node, "lineno", None) is not None:
            location["line"] = node.lineno
        return {**result, "status": UNKNOWN, "reason": reason, "path": [], **location}

    if len(source) > MAX_SOURCE:
        return unknown("SOURCE_BYTES_EXCEEDED")
    try:
        module = ast.parse(source.decode("utf-8"))
    except UnicodeDecodeError:
        return unknown("INVALID_UTF8")
    except SyntaxError as exc:
        return unknown("INVALID_SYNTAX", exc)
    except RecursionError:
        return unknown("PARSER_RECURSION_LIMIT")
    if sum(1 for _ in ast.walk(module)) > 256:
        return unknown("AST_NODES_EXCEEDED")

    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        return unknown("UNSUPPORTED_MODULE", next(iter(module.body), None))
    function = module.body[0]
    args = function.args
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
        or len(args.args) != 1
        or args.args[0].arg != "source"
        or args.args[0].annotation is not None
    ):
        return unknown("UNSUPPORTED_SIGNATURE", function)

    lines = source_lines(source)

    def evidence(kind, node):
        entry = {
            "kind": kind,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "start_col": node.col_offset,
            "end_col": node.end_col_offset,
        }
        return {**entry, "sha256": digest(segment(lines, entry))}

    def scalar(node):
        return isinstance(node, ast.Constant) and type(node.value) in (
            str,
            int,
            float,
            bool,
            type(None),
        )

    bindings = {"source": [evidence("parameter", args.args[0])]}
    for stmt in function.body[:-1]:
        if (
            not isinstance(stmt, ast.Assign)
            or len(stmt.targets) != 1
            or not isinstance(stmt.targets[0], ast.Name)
            or stmt.targets[0].id == "consume"
        ):
            return unknown("UNSUPPORTED_STATEMENT", stmt)
        value = stmt.value
        if scalar(value):
            path = [evidence("literal_assignment", stmt)]
        elif isinstance(value, ast.Name):
            if value.id not in bindings:
                return unknown("UNRESOLVED_NAME", value)
            path = [*bindings[value.id], evidence("copy_assignment", stmt)]
        else:
            return unknown("UNSUPPORTED_VALUE", value)
        bindings[stmt.targets[0].id] = path

    last = function.body[-1]
    call = last.value if isinstance(last, ast.Expr) else None
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "consume"
        or len(call.args) != 1
        or call.keywords
    ):
        return unknown("UNSUPPORTED_MARKER", last)
    argument = call.args[0]
    if scalar(argument):
        # One entry serves as both literal origin and marker argument.
        path = [evidence("marker_literal", argument)]
    elif isinstance(argument, ast.Name):
        if argument.id not in bindings:
            return unknown("UNRESOLVED_NAME", argument)
        path = [*bindings[argument.id], evidence("marker_argument", argument)]
    else:
        return unknown("UNSUPPORTED_VALUE", argument)

    status = FLOW if path[0]["kind"] == "parameter" else NEGATIVE
    reason = "PARAMETER_ORIGIN" if status == FLOW else "LITERAL_ORIGIN"
    return {**result, "status": status, "reason": reason, "path": path}


def reject_aliases(path):
    # These checks guard fixed local paths without supporting concurrent hostile mutation.
    if any(part.is_symlink() or part.is_junction() for part in (*path.parents, path)):
        raise ExperimentError("PATH_ALIAS")


def bounded_read(path):
    reject_aliases(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ExperimentError("NONREGULAR_FIXTURE")
    with path.open("rb") as stream:
        data = stream.read(MAX_SOURCE + 1)
    if len(data) > MAX_SOURCE:
        raise ExperimentError("FIXTURE_BYTES_EXCEEDED")
    return data


def git_commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            timeout=2,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def main():
    if len(sys.argv) != 1:
        print("This experiment accepts no arguments.", file=sys.stderr)
        return 2

    start = time.monotonic()
    run_id = str(uuid.uuid4())
    run_dir = OUTPUT_ROOT / run_id
    try:
        reject_aliases(run_dir)
        run_dir.mkdir(parents=True, exist_ok=False)
    except ExperimentError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError:
        print("RUN_DIRECTORY_CREATION_FAILED", file=sys.stderr)
        return 1
    cases = {}
    report = {
        "schema_version": VERSION,
        "analyzer_version": VERSION,
        "python_version": platform.python_version(),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "git_commit": git_commit(),
        "run_id": run_id,
        "oracle_sha256": None,
        "corpus_sha256": {},
        "cases": cases,
    }
    expected = {}
    errors = []
    try:
        oracle_bytes = bounded_read(CORPUS / "oracle.json")
        report["oracle_sha256"] = digest(oracle_bytes)
        oracle = json.loads(oracle_bytes)
        if (
            not isinstance(oracle, dict)
            or oracle.keys() != set(CASE_IDS)
            or any(oracle[case] not in (FLOW, NEGATIVE, UNKNOWN) for case in CASE_IDS)
            or Counter(oracle.values()) != {FLOW: 4, NEGATIVE: 4, UNKNOWN: 4}
        ):
            raise ExperimentError("INVALID_ORACLE")
        expected = oracle
        # The 12 fixed names and per-file read cap bound aggregate bytes below 256 KiB.
        for case in CASE_IDS:
            path = CORPUS / f"{case}.py"
            source = bounded_read(path)
            file_path = path.relative_to(ROOT).as_posix()
            report["corpus_sha256"][file_path] = digest(source)
            result = analyze_source(source, file_path=file_path)
            cases[case] = {"expected": expected[case], "observed": result}
            if result["status"] != expected[case]:
                errors.append(f"{case}:ORACLE_MISMATCH")
            lines = source_lines(source)
            if bool(result["path"]) != (result["status"] != UNKNOWN) or any(
                digest(segment(lines, item)) != item["sha256"]
                for item in result["path"]
            ):
                errors.append(f"{case}:INVALID_EVIDENCE")
    except ExperimentError as exc:
        errors.append(str(exc))
    except OSError:
        errors.append("FIXTURE_IO_ERROR")
    except (ValueError, RecursionError):
        errors.append("INVALID_ORACLE")

    report["counts"] = {
        "total": len(CASE_IDS),
        "matched": sum(
            case["expected"] == case["observed"]["status"] for case in cases.values()
        ),
        "expected": dict(Counter(expected.values())),
        "observed": dict(
            Counter(case["observed"]["status"] for case in cases.values())
        ),
    }
    report["elapsed_seconds"] = time.monotonic() - start
    if report["elapsed_seconds"] > 10:
        errors.append("ELAPSED_BUDGET_EXCEEDED")
    report["errors"] = errors
    encoded = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    if len(encoded) > MAX_ARTIFACT:
        errors.append("ARTIFACT_BYTES_EXCEEDED")
        report["cases"] = {}
        encoded = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    output = run_dir / "result.json"
    try:
        with output.open("xb") as stream:
            stream.write(encoded)
    except OSError:
        print("ARTIFACT_WRITE_FAILED", file=sys.stderr)
        return 1
    print(output)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
