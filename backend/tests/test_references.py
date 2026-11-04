import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from lazarus_sentinel import bundle, explanations, investigation, meta_provider, references, service
from lazarus_sentinel.bundle import export_demo_bundle, parse_json, validate_bundle
from lazarus_sentinel.cli import SAFE_CODES, main
from lazarus_sentinel.references import (
    RULE_REFERENCES,
    lookup_references,
    transport_payload,
    validate_references,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    shutil.copytree(service.FIXTURE_ROOT, tmp_path / "fixtures" / "fastapi_demo")
    for module in (bundle, explanations, investigation, references, service):
        monkeypatch.setattr(module, "WORKSPACE", tmp_path)
    return tmp_path


def recorded(root, result):
    return json.loads((root / result["artifact_path"]).read_bytes())


def test_disabled_by_default():
    assert lookup_references("LS-AUTH-001") == {"status": "DISABLED", "provider": "disabled"}


def test_frontend_static_mapping_matches_backend():
    mirrored = json.loads((ROOT / "frontend" / "src" / "rule-references.json").read_text())
    assert mirrored == {rule: value["references"] for rule, value in RULE_REFERENCES.items()}


def test_search_input_is_fixed_question_without_code():
    request = parse_json(transport_payload("LS-AUTH-001"))
    assert request["input"] == RULE_REFERENCES["LS-AUTH-001"]["question"]
    fixture_text = "".join(p.read_text() for p in service.FIXTURE_ROOT.rglob("*.py"))
    assert "def " not in request["input"] and request["input"] not in fixture_text


def test_mock_references_export_in_bundle(workspace):
    scan = service.scan("fixture:fastapi-demo", workspace / "artifacts")
    result = lookup_references("LS-AUTH-001", "mock")
    value = validate_references(recorded(workspace, result))
    assert value.generation == "mock" and len(value.citations) == 2
    exported = export_demo_bundle(scan["scan_id"], references_id=result["reference_id"])
    directory = workspace / exported["artifact_dir"]
    manifest = parse_json((directory / "bundle.json").read_bytes())
    payloads = {name: (directory / name).read_bytes() for name in manifest["artifacts"]}
    assert set(payloads) == {"graph.json", "references.json"}
    validate_bundle(manifest, payloads)
    assert not (workspace / "artifacts" / "agent-budget.sqlite3").exists()


def test_cli_references(workspace, capsys):
    assert main(["references", "--rule-id", "LS-AUTH-001"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "DISABLED"
    assert main(["references", "--rule-id", "LS-NOPE", "--provider", "mock"]) == 1
    assert json.loads(capsys.readouterr().out)["diagnostic_codes"] == ["UNKNOWN_RULE"]


@pytest.mark.parametrize(
    "mutate,code",
    [
        (lambda v: v["citations"][0].update(url="https://evil.example/cwe"), "UNTRUSTED_CITATION"),
        (lambda v: v["citations"][0].update(url="http://cwe.mitre.org/x"), ""),
        (lambda v: v.update(request_sha256="0" * 64), "REFERENCES_REQUEST_MISMATCH"),
        (lambda v: v.update(rule_id="LS-OTHER"), "UNKNOWN_RULE"),
    ],
)
def test_tampered_references_rejected(workspace, mutate, code):
    value = recorded(workspace, lookup_references("LS-AUTH-001", "mock"))
    mutate(value)
    with pytest.raises(ValueError, match=code or "url"):
        validate_references(value)


def search_call(*queries):
    return {
        "type": "web_search_call",
        "id": "ws",
        "action": {"type": "search", "query": "q", "queries": list(queries)},
    }


def response(citations, status="completed", searches=1, calls=None):
    calls = calls if calls is not None else [search_call(f"query {i}") for i in range(searches)]
    return {
        "status": status,
        "usage": {"input_tokens": 400, "output_tokens": 100, "total_tokens": 500},
        "output": calls
        + [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": "Missing authorization lets callers reach protected operations.",
                        "annotations": [
                            {"type": "url_citation", "url": u, "title": t} for u, t in citations
                        ],
                    }
                ],
            }
        ],
    }


def live(monkeypatch, result):
    paths = []

    def transport(payload, key, path):
        paths.append(path)
        return result

    monkeypatch.setenv("MODEL_API_KEY", "fake-test-key")
    monkeypatch.setattr(meta_provider, "bounded_transport", transport)
    return paths


def test_live_keeps_only_allowlisted_citations_and_bills_search(workspace, monkeypatch):
    paths = live(
        monkeypatch,
        response(
            [
                ("https://cwe.mitre.org/data/definitions/862.html", "CWE-862"),
                ("https://cwe.mitre.org/data/definitions/862.html", "duplicate"),
                ("https://evil.example/owasp.org", "spoof"),
                ("http://owasp.org/insecure", "plain http"),
                ("https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/", "A01"),
            ],
            searches=2,
        ),
    )
    value = validate_references(recorded(workspace, lookup_references("LS-AUTH-001", "meta")))
    assert paths == ["/v1/responses"]
    assert [c.title for c in value.citations] == ["CWE-862", "A01"]
    assert value.generation == "live" and value.usage.searches == 2
    assert value.usage.estimated_micro_usd == 500 + 425 + 5000
    with sqlite3.connect(workspace / "artifacts" / "agent-budget.sqlite3") as db:
        assert db.execute("SELECT actual,state FROM attempts").fetchall() == [(5925, "SETTLED")]


@pytest.mark.parametrize(
    "result,code",
    [
        (response([("https://evil.example/", "x")]), "NO_TRUSTED_CITATIONS"),
        (response([], status="failed"), "META_INVALID_RESPONSE"),
        (response([("https://cwe.mitre.org/a", "a")], searches=4), "META_INVALID_RESPONSE"),
        ({"status": "completed", "usage": {}, "output": []}, "META_SEARCH_TOKEN_USAGE"),
        ({"usage": {}, "output": {"untrusted": "private text"}}, "META_SEARCH_OUTPUT_SHAPE"),
        (
            {"usage": {"input_tokens": 10, "output_tokens": 4096}, "output": []},
            "META_SEARCH_SETTLEMENT_REJECTED",
        ),
    ],
)
def test_live_failures_write_nothing(workspace, monkeypatch, result, code):
    live(monkeypatch, result)
    with pytest.raises(ValueError, match=code):
        lookup_references("LS-AUTH-001", "meta")
    assert code in SAFE_CODES
    assert not (workspace / "artifacts" / "references").exists()


@pytest.mark.parametrize(
    "overrides",
    [
        {"include": ["web_search_call.results"]},
        {"tools": [{"type": "web_search", "search_context_size": "high"}]},
        {"store": True},
        {"input": ["structured"]},
    ],
)
def test_generate_search_rejects_unreviewed_requests(monkeypatch, tmp_path, overrides):
    monkeypatch.setenv("MODEL_API_KEY", "fake-test-key")
    monkeypatch.setattr(meta_provider, "bounded_transport", lambda *a: pytest.fail("no transport"))
    payload = json.dumps({**parse_json(transport_payload("LS-AUTH-001")), **overrides}).encode()
    with pytest.raises(ValueError, match="INVALID_META_REQUEST"):
        meta_provider.generate_search(payload, tmp_path / "agent.sqlite3")
    assert not (tmp_path / "agent.sqlite3").exists()


def test_multi_query_search_action_is_billed_per_query(workspace, monkeypatch):
    citation = [("https://cwe.mitre.org/data/definitions/862.html", "CWE-862")]
    live(monkeypatch, response(citation, calls=[search_call("cwe 862", "owasp a01")]))
    value = validate_references(recorded(workspace, lookup_references("LS-AUTH-001", "meta")))
    assert value.usage.searches == 2


def test_legacy_search_query_settles_as_one_query(workspace, monkeypatch):
    citation = [("https://cwe.mitre.org/data/definitions/862.html", "CWE-862")]
    call = {"type": "web_search_call", "id": "ws", "action": {"type": "search", "query": "CWE-862"}}
    live(monkeypatch, response(citation, calls=[call]))
    value = validate_references(recorded(workspace, lookup_references("LS-AUTH-001", "meta")))
    assert value.usage.searches == 1
    with sqlite3.connect(workspace / "artifacts" / "agent-budget.sqlite3") as db:
        assert db.execute("SELECT actual,state FROM attempts").fetchall() == [(3425, "SETTLED")]


def test_query_cap_counts_queries_and_still_settles(workspace, monkeypatch):
    citation = [("https://cwe.mitre.org/data/definitions/862.html", "CWE-862")]
    live(monkeypatch, response(citation, calls=[search_call("a", "b", "c", "d")]))
    with pytest.raises(ValueError, match="META_INVALID_RESPONSE"):
        lookup_references("LS-AUTH-001", "meta")
    with sqlite3.connect(workspace / "artifacts" / "agent-budget.sqlite3") as db:
        assert db.execute("SELECT actual,state FROM attempts").fetchall() == [
            (500 + 425 + 10000, "SETTLED")
        ]


@pytest.mark.parametrize(
    "action",
    [
        None,
        {"type": "search"},
        {"type": "search", "query": " "},
        {"type": "search", "query": "CWE-862", "queries": [1]},
    ],
)
def test_unknown_search_billing_retains_reservation(workspace, monkeypatch, action):
    paths = live(
        monkeypatch,
        response([], calls=[{"type": "web_search_call", "id": "ws", "action": action}]),
    )
    with pytest.raises(ValueError, match="^META_SEARCH_QUERY_SHAPE$"):
        lookup_references("LS-AUTH-001", "meta")
    with pytest.raises(ValueError, match="BUDGET_RECONCILIATION_REQUIRED"):
        lookup_references("LS-AUTH-001", "meta")
    assert paths == ["/v1/responses"]
    assert not (workspace / "artifacts" / "references").exists()
