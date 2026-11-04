"""Exercise the controlled trust policy and byte-bound declarations."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def trust(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("assess_trust", ROOT / "scripts/assess_trust.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_oracle_and_exact_evidence(trust, monkeypatch, tmp_path):
    policy = (trust.CORPUS / "policy.json").read_bytes()
    oracle = json.loads((trust.CORPUS / "oracle.json").read_bytes())
    monkeypatch.setattr(trust, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(trust.sys, "argv", ["assess_trust.py"])
    assert trust.main() == 0
    report = json.loads(next(tmp_path.glob("*/result.json")).read_bytes())
    assert report["oracle_mismatches"] == []
    assert report["policy_sha256"] == hashlib.sha256(policy).hexdigest()
    for name, expected in oracle.items():
        source = (trust.CORPUS / f"{name}.py").read_bytes()
        result = report["cases"][name]
        assert result["outcome"] == expected
        assert result["source_sha256"] == hashlib.sha256(source).hexdigest()
        assert result["policy_sha256"] == report["policy_sha256"]
        lines = source.splitlines()
        if expected == "NEEDS_CONTEXT":
            assert result["transition"] is None
            assert result["evidence"] == []
            continue
        assert result["evidence"][-1]["kind"] == "handoff_declaration"
        for item in result["evidence"]:
            assert item["start_line"] == item["end_line"]
            segment = lines[item["start_line"] - 1][item["start_col"] : item["end_col"]]
            assert item["sha256"] == hashlib.sha256(segment).hexdigest()
    assert report["cases"]["wrong_scope"]["handling_destination_zone"] == "internal"
    assert report["cases"]["handled"]["handling_destination_zone"] == "partner"


@pytest.mark.parametrize(
    "body",
    [
        'other_helper("partner")\n    handoff("partner")',
        'handoff("partner")\n    check_consent("partner")',
        'handoff(destination="partner")',
        'handoff("unknown")',
        'client.handoff("partner")',
        'handoff("partner", "internal")',
    ],
)
def test_unsupported_marker_forms_are_not_candidates(trust, body):
    policy = (trust.CORPUS / "policy.json").read_bytes()
    result = trust.assess_source(
        f"def transfer():\n    {body}\n".encode(), policy, file_path="held_out.py"
    )
    assert result["outcome"] == "NEEDS_CONTEXT"
    assert not result["evidence"]


def test_reject_changed_or_duplicate_policy(trust):
    raw = (trust.CORPUS / "policy.json").read_bytes()
    with pytest.raises(trust.spike.ExperimentError, match="UNSUPPORTED_TRUST_POLICY"):
        trust.load_policy(raw.replace(b'"partner"', b'"external"'))
    with pytest.raises(trust.spike.ExperimentError, match="INVALID_TRUST_POLICY"):
        trust.load_policy(
            raw.replace(b'"policy_version": "1"', b'"policy_version":"2","policy_version":"1"')
        )


@pytest.mark.parametrize(
    ("body", "outcome", "evidence_kinds"),
    [
        ("handoff('partner')", "CANDIDATE", ["handoff_declaration"]),
        (
            "check_consent('partner')\n    handoff('partner')",
            "NO_CANDIDATE_IN_SUBSET",
            ["handling_declaration", "handoff_declaration"],
        ),
        ("handoff(destination())", "NEEDS_CONTEXT", []),
    ],
)
def test_held_out_trust_projection_inputs(trust, body, outcome, evidence_kinds):
    policy = (trust.CORPUS / "policy.json").read_bytes()
    source = f"# café\ndef transfer():\n    {body}\n".replace("\n", "\r\n").encode()
    result = trust.assess_source(source, policy, file_path="held_out.py")
    assert result["outcome"] == outcome
    assert [item["kind"] for item in result["evidence"]] == evidence_kinds
    for item in result["evidence"]:
        assert item["start_line"] >= 3
        lines = source.splitlines()
        span = lines[item["start_line"] - 1][item["start_col"] : item["end_col"]]
        assert item["sha256"] == hashlib.sha256(span).hexdigest()
