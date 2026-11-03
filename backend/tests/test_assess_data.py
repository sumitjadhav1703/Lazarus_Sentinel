"""Test the fixed DATA policy and its separate evidence report."""

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def data_runner(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    return importlib.import_module("assess_data")


def test_fixed_assessment_is_separate_and_keeps_previous_results(
    data_runner, monkeypatch, tmp_path
):
    monkeypatch.setattr(data_runner, "OUTPUT_ROOT", tmp_path)
    first = data_runner.assess()
    first_bytes = first.read_bytes()
    second = data_runner.assess()
    assert first != second
    assert first.read_bytes() == first_bytes
    report = json.loads(first_bytes)
    assert report["counts"] == {
        "CANDIDATE": 4,
        "NO_CANDIDATE_IN_SUBSET": 4,
        "NEEDS_CONTEXT": 4,
    }
    expected = {"P": "CANDIDATE", "C": "NO_CANDIDATE_IN_SUBSET", "U": "NEEDS_CONTEXT"}
    for name, case in report["cases"].items():
        assert case["outcome"] == expected[name[0]]
        assert (case.get("confidence") == "LOW") == (name[0] == "P")
        assert bool(case["path"]) == (name[0] != "U")
    assert report["cases"] == json.loads(second.read_bytes())["cases"]


@pytest.mark.parametrize(
    ("data", "code"),
    [
        (b"{", "INVALID_DATA_POLICY"),
        (b'{"rule_id":"LS-DATA-001","rule_id":"LS-DATA-001"}', "INVALID_DATA_POLICY"),
        (
            b'{"rule_id":"LS-DATA-001","required_argument_origin":"parameter"}',
            "UNSUPPORTED_DATA_POLICY",
        ),
    ],
)
def test_policy_does_not_accept_malformed_or_different_contract(data_runner, data, code):
    with pytest.raises(ValueError, match=code):
        data_runner.load_policy(data)


def test_tampered_span_prevents_report_publication(data_runner, monkeypatch, tmp_path):
    analyze = data_runner.spike.analyze_source

    def tamper(source, *, file_path):
        result = analyze(source, file_path=file_path)
        result["path"][0]["sha256"] = "0" * 64
        return result

    monkeypatch.setattr(data_runner, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(data_runner.spike, "analyze_source", tamper)
    with pytest.raises(ValueError, match="INVALID_DATA_EVIDENCE"):
        data_runner.assess()
    assert not list(tmp_path.iterdir())
