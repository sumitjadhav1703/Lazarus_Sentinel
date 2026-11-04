"""Verify the separate synthetic actor/action/resource assessment."""

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    return importlib.import_module("assess_auth_context")


def test_fixed_policy_distinguishes_actor_action_resource_and_unknown(
    runner, monkeypatch, tmp_path
):
    monkeypatch.setattr(runner, "OUTPUT_ROOT", tmp_path)
    first = runner.assess()
    first_bytes = first.read_bytes()
    second = runner.assess()
    assert first != second
    assert first.read_bytes() == first_bytes
    report = json.loads(first_bytes)
    assert report["counts"] == {
        "CANDIDATE": 4,
        "DECLARATION_RECOGNIZED": 1,
        "NEEDS_CONTEXT": 1,
    }
    cases = report["cases"]
    for name, diagnostic in {
        "missing": "DECLARATION_MISSING",
        "wrong_actor": "ACTOR_MISMATCH",
        "wrong_action": "ACTION_MISMATCH",
        "wrong_resource": "RESOURCE_MISMATCH",
    }.items():
        case = cases[name]
        assert (case["outcome"], case["confidence"]) == ("CANDIDATE", "LOW")
        assert case["diagnostics"] == [diagnostic]
        assert case["evidence"][-1]["kind"] == "protected_operation"
    assert cases["recognized"]["outcome"] == "DECLARATION_RECOGNIZED"
    assert cases["recognized"]["diagnostics"] == []
    assert cases["dynamic"]["outcome"] == "NEEDS_CONTEXT"
    assert cases["dynamic"]["evidence"] == []
    assert report["cases"] == json.loads(second.read_bytes())["cases"]


@pytest.mark.parametrize(
    "body",
    [
        b'    authorize(actor, "export", other)\n    export(resource)\n',
        b'    if enabled:\n        authorize(actor, "export", resource)\n    export(resource)\n',
        b'    authorize(actor, "export", resource)\n    export(other)\n',
        b'    export(resource)\n    authorize(actor, "export", resource)\n',
    ],
)
def test_opaque_actor_resource_or_declaration_order_remains_unknown(runner, body):
    source = b"def case(actor, resource):\n" + body
    result = runner.analyze(source, "held_out.py", runner.POLICY)
    assert result["outcome"] == "NEEDS_CONTEXT"
    assert result["evidence"] == []


@pytest.mark.parametrize(
    ("data", "code"),
    [
        (b"{", "INVALID_AUTH_CONTEXT_POLICY"),
        (b'{"action":"export","action":"export"}', "INVALID_AUTH_CONTEXT_POLICY"),
        (b'{"action":"preview"}', "UNSUPPORTED_AUTH_CONTEXT_POLICY"),
    ],
)
def test_policy_rejects_malformed_or_different_contract(runner, data, code):
    with pytest.raises(ValueError, match=code):
        runner.load_policy(data)


def test_tampered_evidence_prevents_publication(runner, monkeypatch, tmp_path):
    analyze = runner.analyze

    def tamper(source, file_path, policy):
        result = analyze(source, file_path, policy)
        result["evidence"][-1]["sha256"] = "0" * 64
        return result

    monkeypatch.setattr(runner, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(runner, "analyze", tamper)
    with pytest.raises(ValueError, match="INVALID_AUTH_CONTEXT_EVIDENCE"):
        runner.assess()
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    ("declaration", "outcome", "diagnostics"),
    [
        ("authorize(actor, 'préview', resource)", "CANDIDATE", ["ACTION_MISMATCH"]),
        ("authorize(actor, 'export', resource)", "DECLARATION_RECOGNIZED", []),
        ("authorize(actor, action(), resource)", "NEEDS_CONTEXT", None),
    ],
)
def test_held_out_auth_projection_inputs(runner, declaration, outcome, diagnostics):
    source = f"def case(actor, resource):\r\n    {declaration}\r\n    export(resource)\r\n".encode()
    result = runner.analyze(source, "held_out.py", runner.POLICY)
    assert result["outcome"] == outcome
    assert result.get("diagnostics") == diagnostics
    runner.validate_evidence(source, result["evidence"])
    if diagnostics is None:
        assert result["evidence"] == []
    else:
        assert [item["kind"] for item in result["evidence"]] == [
            "actor_parameter",
            "resource_parameter",
            "authorization_declaration",
            "protected_operation",
        ]
