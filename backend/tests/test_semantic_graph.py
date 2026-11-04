import hashlib
import importlib
from copy import deepcopy
from pathlib import Path

import pytest

from lazarus_sentinel.bundle import parse_json
from lazarus_sentinel.semantic_graph import project_data, validate_data_graph

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def exporter(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    return importlib.import_module("export_semantic_graph")


def test_fixed_export_keeps_unknowns_out_of_findings(exporter, monkeypatch, tmp_path):
    monkeypatch.setattr(exporter, "OUTPUT_ROOT", tmp_path)
    first = exporter.export_data_graph()
    second = exporter.export_data_graph()
    assert first != second
    assert first.read_bytes() == second.read_bytes()
    graph = parse_json(first.read_bytes())
    assert len(graph["findings"]) == 4
    assert [row["status"] for row in graph["coverage"]].count("UNKNOWN") == 4
    assert [row["status"] for row in graph["coverage"]].count("NO_FLOW_IN_SUBSET") == 4
    assert all(edge["type"] == "FLOWS_TO" for edge in graph["edges"])
    assert all(edge["fact_status"] == "OBSERVED" for edge in graph["edges"])


@pytest.mark.parametrize(
    ("body", "status", "findings"),
    [
        ("    proxy = source\n    consume(proxy)\n", "FLOW_OBSERVED", 1),
        ("    proxy = 'fixed'\n    consume(proxy)\n", "NO_FLOW_IN_SUBSET", 0),
        ("    proxy = wrap(source)\n    consume(proxy)\n", "UNKNOWN", 0),
    ],
)
def test_held_out_data_cases(exporter, body, status, findings):
    path = "held_out.py"
    source = ("def case(source):\n" + body).encode()
    policy = exporter.spike.bounded_read(exporter.spike.CORPUS / "data_policy.json")
    exporter.load_policy(policy)
    observed = exporter.spike.analyze_source(source, file_path=path)
    exporter.validate_evidence(source, observed)
    graph = project_data(policy, {path: source}, {path: observed})
    assert graph["coverage"] == [{"path": path, "status": status}]
    assert len(graph["findings"]) == findings


def test_exact_evidence_and_paths_reject_tampering():
    source = b"def case(source):\n    consume(source)\n"
    path = "fixture.py"
    sha = hashlib.sha256(b"source").hexdigest()
    observations = {
        path: {
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "status": "FLOW_OBSERVED",
            "path": [
                {
                    "kind": "parameter",
                    "start_line": 1,
                    "end_line": 1,
                    "start_col": 9,
                    "end_col": 15,
                    "sha256": sha,
                },
                {
                    "kind": "marker_argument",
                    "start_line": 2,
                    "end_line": 2,
                    "start_col": 12,
                    "end_col": 18,
                    "sha256": sha,
                },
            ],
        }
    }
    graph = project_data(b"policy", {path: source}, observations)
    validate_data_graph(graph, b"policy", {path: source}, observations)
    assert graph["evidence"][0]["excerpt_hash"] == (
        "sha256:" + hashlib.sha256(source.splitlines(keepends=True)[0]).hexdigest()
    )
    corrupt = deepcopy(graph)
    corrupt["edges"][0]["source"] = corrupt["edges"][0]["target"]
    with pytest.raises(ValueError, match="INVALID_CANONICAL_DATA_GRAPH"):
        validate_data_graph(corrupt, b"policy", {path: source}, observations)
    observations[path]["path"][1]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="INVALID_DATA_SPAN"):
        project_data(b"policy", {path: source}, observations)
