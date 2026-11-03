"""Run the evidence assistant on one fixed synthetic fixture and verify its bundle."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "src"))

from lazarus_sentinel.bundle import (
    export_json_schemas,
    load_committed_graph,
    parse_json,
    read_bounded,
    validate_bundle,
)
from lazarus_sentinel.cli import SAFE_CODES


def cli(*args: str, expected: int = 0) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "lazarus_sentinel", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != expected:
        try:
            codes = json.loads(result.stdout)["diagnostic_codes"]
            if (
                isinstance(codes, list)
                and codes
                and all(type(code) is str and code in SAFE_CODES for code in codes)
            ):
                raise DemoCommandError(codes)
        except (KeyError, TypeError, ValueError):
            pass
        raise ValueError("DEMO_COMMAND_FAILED")
    return json.loads(result.stdout)


class DemoCommandError(Exception):
    def __init__(self, codes: list[str]):
        super().__init__("DEMO_COMMAND_FAILED")
        self.codes = codes


def prepare(*, verify_only: bool = False, provider: str = "mock") -> dict:
    if provider not in {"mock", "meta"} or (provider == "meta" and not verify_only):
        raise ValueError("INVALID_PROVIDER")
    budget = ROOT / "artifacts" / "model-budget.sqlite3"
    budget_before = (
        budget.read_bytes() if provider == "mock" and budget.exists() else None
    )
    scan = cli("scan", "--target", "fixture:fastapi-demo", expected=2)
    loaded = load_committed_graph(scan["scan_id"])
    finding = next(f for f in loaded.graph.findings if f.confidence == "LOW")
    disabled = cli("explain", "--scan-id", scan["scan_id"], "--finding-id", finding.id)
    if disabled != {"status": "DISABLED", "provider": "disabled"}:
        raise ValueError("INVALID_DISABLED_RESULT")
    annotation = cli(
        "explain",
        "--scan-id",
        scan["scan_id"],
        "--finding-id",
        finding.id,
        "--provider",
        provider,
    )
    exported = cli(
        "demo",
        "export",
        "--scan-id",
        scan["scan_id"],
        "--annotation-id",
        annotation["annotation_id"],
    )
    if (
        provider == "mock"
        and (budget.read_bytes() if budget.exists() else None) != budget_before
    ):
        raise ValueError("MOCK_MODIFIED_LIVE_BUDGET")
    if load_committed_graph(scan["scan_id"]).graph_bytes != loaded.graph_bytes:
        raise ValueError("CANONICAL_GRAPH_CHANGED")
    source = ROOT / exported["artifact_dir"]
    manifest_bytes = read_bounded(source / "bundle.json")
    manifest = parse_json(manifest_bytes)
    payloads = {name: read_bounded(source / name) for name in manifest["artifacts"]}
    validate_bundle(manifest, payloads)
    if payloads["graph.json"] != loaded.graph_bytes:
        raise ValueError("GRAPH_BYTES_CHANGED")
    recorded = parse_json(payloads["explanations.json"])["annotations"][0]
    if (
        recorded["annotation_id"] != annotation["annotation_id"]
        or recorded["provider"] != provider
    ):
        raise ValueError("ANNOTATION_BINDING_MISMATCH")
    result = {
        **exported,
        "annotation_id": annotation["annotation_id"],
        "finding_id": finding.id,
        "provider": provider,
        "model": recorded["model"],
        "generation": recorded["generation"],
        "review_status": recorded["review_status"],
    }
    if verify_only:
        return result

    destination = ROOT / "frontend" / "public" / "demo" / "v1"
    destination.mkdir(parents=True, exist_ok=True)
    # Only fixed reviewed bundle filenames are ever copied into the viewer.
    for name, data in {"bundle.json": manifest_bytes, **payloads}.items():
        (destination / name).write_bytes(data)
    schemas = ROOT / "frontend" / "src" / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for name, schema in export_json_schemas().items():
        (schemas / name).write_text(json.dumps(schema, sort_keys=True, indent=2) + "\n")
    return {**result, "viewer_bundle": str(destination)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Create and validate a demo bundle under artifacts/ without updating the viewer.",
    )
    parser.add_argument("--provider", choices=("mock", "meta"), default="mock")
    args = parser.parse_args()
    if args.provider == "meta" and not args.verify_only:
        parser.error("--provider meta requires --verify-only")
    try:
        print(
            json.dumps(
                prepare(verify_only=args.verify_only, provider=args.provider),
                sort_keys=True,
            )
        )
    except DemoCommandError as error:
        print(json.dumps({"status": "FAILED", "diagnostic_codes": error.codes}))
        raise SystemExit(1) from None
    except Exception:  # noqa: BLE001 - preparation must not echo target/provider exception text.
        print(
            json.dumps(
                {"status": "FAILED", "diagnostic_codes": ["DEMO_PREPARATION_FAILED"]}
            )
        )
        raise SystemExit(1) from None
