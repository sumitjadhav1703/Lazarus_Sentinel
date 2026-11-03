"""Verify the frozen synthetic provenance experiment."""

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "fixtures" / "semantic_spike"


@pytest.fixture
def spike():
    script = ROOT / "scripts" / "semantic_spike.py"
    assert script.is_file(), "semantic experiment is missing"
    spec = importlib.util.spec_from_file_location("semantic_spike", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reconstructed(source, result):
    lines = re.split(rb"(?<=\n)|(?<=\r)(?!\n)", source)
    segments = []
    for entry in result["path"]:
        start, end = entry["start_line"] - 1, entry["end_line"] - 1
        left, right = entry["start_col"], entry["end_col"]
        assert 0 <= start <= end < len(lines)
        assert 0 <= left < len(lines[start])
        assert 0 < right <= len(lines[end])
        segment = b"".join(lines[start : end + 1])[left : sum(map(len, lines[start:end])) + right]
        assert segment and hashlib.sha256(segment).hexdigest() == entry["sha256"]
        segments.append(segment)
    return segments


def test_oracle_and_deterministic_exact_paths(spike):
    expected_paths = {
        "P01": [b"source", b"source"],
        "P02": [b"source", b"copy = source", b"copy"],
        "P03": [b"source", b"a = source", b"b = a", b"b"],
        "P04": [b"source", b"a = source", b"a"],
        "C01": [b'"fixed"'],
        "C02": [b'copy = "fixed"', b"copy"],
        "C03": [b'source = "fixed"', b"source"],
        "C04": [b'a = "fixed"', b"b = a", b"b"],
    }
    oracle = json.loads((CORPUS / "oracle.json").read_bytes())
    assert len(oracle) == 12
    for case, expected in oracle.items():
        file_path = f"{case}.py"
        source = (CORPUS / file_path).read_bytes()
        result = spike.analyze_source(source, file_path=file_path)
        assert result == spike.analyze_source(source, file_path=file_path)
        assert result["status"] == expected
        assert result["file_path"] == file_path
        assert result["source_sha256"] == hashlib.sha256(source).hexdigest()
        assert reconstructed(source, result) == expected_paths.get(case, [])


@pytest.mark.parametrize(
    "source",
    [
        b"\xff",
        b"def case(source):\n consume(",
        b"def case(source):\n def nested():\n  copy = source\n consume(source)",
        b"def case(source):\n consume = source\n consume(source)",
        b"def case(source):\n a = b = source\n consume(a)",
        b" " * (16 * 1024 + 1),
        b"def case(source):\n" + b" a = source\n" * 128 + b" consume(a)",
    ],
)
def test_rejects_invalid_or_unsupported_sources(spike, source):
    result = spike.analyze_source(source, file_path="extra.py")
    assert result["status"] == "UNKNOWN"
    assert result["reason"]
    assert result["path"] == []


def test_evidence_uses_utf8_byte_columns(spike):
    source = "def case(source):\r\n café = 'é'\r\n consume(café)".encode()
    result = spike.analyze_source(source, file_path="unicode.py")
    assert result["status"] == "NO_FLOW_IN_SUBSET"
    assert reconstructed(source, result) == ["café = 'é'".encode(), "café".encode()]
    assert result["path"][-1]["end_col"] == 14


def test_runner_preserves_unique_runs(spike, tmp_path, monkeypatch):
    monkeypatch.setattr(spike, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["semantic_spike.py"])
    assert spike.main() == 0
    assert spike.main() == 0
    runs = list(tmp_path.glob("*/result.json"))
    assert len(runs) == 2
    first, second = (json.loads(path.read_bytes()) for path in runs)
    assert first["run_id"] != second["run_id"]
    for report in (first, second):
        assert report["counts"]["matched"] == report["counts"]["total"] == 12
        assert report["counts"]["observed"]["UNKNOWN"] == 4
    assert first["cases"] == second["cases"]


def test_runner_rejects_symlink_output_parent(spike, tmp_path, monkeypatch):
    outside = tmp_path / "outside"
    outside.mkdir()
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError):
        pytest.skip("directory symlinks unavailable")
    monkeypatch.setattr(spike, "OUTPUT_ROOT", alias / "semantic-spike")
    monkeypatch.setattr("sys.argv", ["semantic_spike.py"])
    assert spike.main() != 0
    assert list(outside.iterdir()) == []
