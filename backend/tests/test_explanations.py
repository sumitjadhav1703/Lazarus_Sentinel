import pytest

from lazarus_sentinel.explanations import explain_finding


def test_disabled_has_no_effects():
    assert explain_finding("invalid", "invalid") == {"status": "DISABLED", "provider": "disabled"}


def test_unknown_provider_rejected():
    with pytest.raises(ValueError):
        explain_finding("invalid", "invalid", "other")


import json

from test_bundle import committed_scan as _committed_scan

from lazarus_sentinel.bundle import export_demo_bundle, load_committed_graph
from lazarus_sentinel.explanations import build_request, validate_annotation


@pytest.fixture
def committed_scan(tmp_path, monkeypatch):
    return _committed_scan.__wrapped__(tmp_path, monkeypatch)


def test_mock_sidecar_binding_and_immutable_scans(committed_scan):
    root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    finding = loaded.graph.findings[0]
    first = explain_finding(scan_id, finding.id, "mock")
    second = explain_finding(scan_id, finding.id, "mock")
    assert first["annotation_id"] != second["annotation_id"]
    annotation = json.loads((root / first["artifact_path"]).read_bytes())
    assert validate_annotation(annotation, loaded).generation == "mock"
    assert load_committed_graph(scan_id).graph_bytes == loaded.graph_bytes
    exported = export_demo_bundle(scan_id, first["annotation_id"])
    assert (root / exported["artifact_dir"] / "explanations.json").is_file()
    assert len(build_request(loaded, finding.id, "mock")["context"]["evidence"]) > 0
    annotation["response"]["evidence_ids"] = ["invented"]
    with pytest.raises(ValueError, match="INVALID_CITATIONS"):
        validate_annotation(annotation, loaded)


@pytest.mark.parametrize(
    "field,value",
    [("request_sha256", "0" * 64), ("graph_sha256", "0" * 64), ("finding_id", "missing")],
)
def test_annotation_rebinding_rejected(committed_scan, field, value):
    root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    result = explain_finding(scan_id, loaded.graph.findings[0].id, "mock")
    annotation = json.loads((root / result["artifact_path"]).read_bytes())
    annotation[field] = value
    with pytest.raises(ValueError):
        validate_annotation(annotation, loaded)


def test_context_and_response_boundaries(committed_scan):
    from lazarus_sentinel.demo_models import ExplanationResponse

    _root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    finding = loaded.graph.findings[0]
    finding.assumptions = ["x" * 20000]
    with pytest.raises(ValueError, match="CONTEXT_SIZE_LIMIT"):
        build_request(loaded, finding.id, "mock")
    base = {"summary": "s", "why_it_matters": "w", "limitations": ["l"], "evidence_ids": ["e"]}
    for change in (
        {"summary": " "},
        {"summary": "x" * 2001},
        {"evidence_ids": ["e", "e"]},
        {"severity": "HIGH"},
    ):
        with pytest.raises(ValueError):
            ExplanationResponse.model_validate(base | change)


def test_cli_rejects_invalid_meta_explanation_without_echoing_content(
    committed_scan, monkeypatch, capsys
):
    from lazarus_sentinel import meta_provider
    from lazarus_sentinel.cli import main

    root, scan_id = committed_scan
    finding_id = load_committed_graph(scan_id).graph.findings[0].id
    monkeypatch.setattr(
        meta_provider, "generate", lambda *_: {"summary": "untrusted-provider-content"}
    )

    assert (
        main(["explain", "--scan-id", scan_id, "--finding-id", finding_id, "--provider", "meta"])
        == 1
    )
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["diagnostic_codes"] == ["META_INVALID_EXPLANATION"]
    assert "untrusted-provider-content" not in stdout
    assert not (root / "artifacts" / "explanations").exists()


@pytest.mark.parametrize(
    "case,code,state",
    [
        ("valid", None, "SETTLED"),
        ("invalid-json", "META_INVALID_RESPONSE", "SETTLED"),
        ("missing-content", "META_INVALID_RESPONSE", "SETTLED"),
        ("truncated", "META_INVALID_RESPONSE", "SETTLED"),
        ("missing-choice", "META_INVALID_RESPONSE", "SETTLED"),
        ("invalid-message", "META_INVALID_RESPONSE", "SETTLED"),
        ("invalid-fields", "META_INVALID_EXPLANATION", "SETTLED"),
        ("tool-call", "META_UNEXPECTED_TOOLS", "SETTLED"),
        ("invalid-citation", "INVALID_CITATIONS", "SETTLED"),
        ("unknown-usage", "UNVERIFIABLE_USAGE", "RESERVED"),
    ],
)
def test_meta_cli_response_and_accounting(committed_scan, monkeypatch, capsys, case, code, state):
    import sqlite3

    from lazarus_sentinel import meta_provider
    from lazarus_sentinel.cli import main

    root, scan_id = committed_scan
    loaded = load_committed_graph(scan_id)
    finding_id = loaded.graph.findings[0].id
    evidence = build_request(loaded, finding_id, "meta")["context"]["evidence"]
    prose = {
        "summary": "Untrusted response text.",
        "why_it_matters": "The synthetic policy protects this operation.",
        "limitations": ["Runtime enforcement is unverified."],
        "evidence_ids": [evidence[0]["id"]],
    }
    if case == "invalid-fields":
        prose["severity"] = "HIGH"
    if case == "invalid-citation":
        prose["evidence_ids"] = ["invented"]
    choice = {"finish_reason": "stop", "message": {"content": json.dumps(prose)}}
    if case == "invalid-json":
        choice["message"]["content"] = '{"summary":"Untrusted response text."'
    if case == "missing-content":
        choice["message"].clear()
    if case == "truncated":
        choice["finish_reason"] = "length"
    if case == "invalid-message":
        choice["message"] = "Untrusted response text."
    if case == "tool-call":
        choice["message"]["tool_calls"] = [{"id": "unexpected"}]
    response = {
        "choices": [] if case == "missing-choice" else [choice],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20},
    }
    if case == "unknown-usage":
        response.pop("usage")
    calls = []

    def transport(*_):
        calls.append(1)
        return response

    monkeypatch.setenv("MODEL_API_KEY", "offline-test-key")
    monkeypatch.setattr(meta_provider, "bounded_transport", transport)
    command = ["explain", "--scan-id", scan_id, "--finding-id", finding_id, "--provider", "meta"]
    assert main(command) == (1 if code else 0)
    output = capsys.readouterr().out
    result = json.loads(output)
    assert "Untrusted response text." not in output
    if code:
        assert result["diagnostic_codes"] == [code]
        assert not (root / "artifacts" / "explanations").exists()
    else:
        annotation = json.loads((root / result["artifact_path"]).read_bytes())
        assert validate_annotation(annotation, loaded).generation == "live"
    if state == "RESERVED":
        assert main(command) == 1
        assert json.loads(capsys.readouterr().out)["diagnostic_codes"] == [
            "BUDGET_RECONCILIATION_REQUIRED"
        ]
    assert calls == [1]
    with sqlite3.connect(root / "artifacts" / "model-budget.sqlite3") as db:
        assert db.execute("select state, actual from attempts").fetchall() == [
            (state, 210 if state == "SETTLED" else None)
        ]


@pytest.mark.parametrize("reject", [False, True])
def test_demo_agent_live_selection_has_one_attempt_and_no_fallback(
    committed_scan, monkeypatch, reject
):
    import importlib.util
    import io
    from contextlib import redirect_stdout
    from pathlib import Path

    from lazarus_sentinel import meta_provider
    from lazarus_sentinel.cli import main

    root, scan_id = committed_scan
    script = Path(__file__).resolve().parents[2] / "scripts" / "prepare_demo.py"
    spec = importlib.util.spec_from_file_location("prepare_demo", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", root)
    calls = []

    def run_cli(*args, expected=0):
        if args[0] == "scan":
            assert args == ("scan", "--target", "fixture:fastapi-demo")
            assert expected == 2
            return {"scan_id": scan_id}
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(args)
        result = json.loads(output.getvalue())
        if code != expected:
            raise module.DemoCommandError(result["diagnostic_codes"])
        return result

    prose_fields = ("summary", "why_it_matters", "limitations", "evidence_ids")

    def transport(payload, _key):
        calls.append(1)
        envelope = json.loads(payload)
        assert envelope["reasoning_effort"] == "minimal"
        assert envelope["max_completion_tokens"] == 1024
        structured = envelope["response_format"]["json_schema"]
        assert structured["strict"] is True
        assert set(structured["schema"]["required"]) == set(prose_fields)
        request = json.loads(envelope["messages"][1]["content"])
        evidence = request["context"]["evidence"][0]["id"]
        content = {
            "summary": "One fixed-fixture candidate.",
            "why_it_matters": "The recorded policy protects this operation.",
            "limitations": ["The static path does not prove runtime enforcement."],
            "evidence_ids": ["invented" if reject else evidence],
        }
        return {
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            "choices": [{"message": {"content": json.dumps(content)}}],
        }

    monkeypatch.setattr(module, "cli", run_cli)
    monkeypatch.setattr(meta_provider, "bounded_transport", transport)
    monkeypatch.setenv("MODEL_API_KEY", "test-only")
    if reject:
        with pytest.raises(module.DemoCommandError) as exc:
            module.prepare(verify_only=True, provider="meta")
        assert exc.value.codes == ["INVALID_CITATIONS"]
        assert not (root / "artifacts" / "demo-bundles").exists()
    else:
        result = module.prepare(verify_only=True, provider="meta")
        assert (result["provider"], result["model"], result["generation"]) == (
            "meta",
            "muse-spark-1.3",
            "live",
        )
        assert result["review_status"] == "UNREVIEWED"
        assert (root / result["artifact_dir"] / "explanations.json").is_file()
    assert calls == [1]
    assert not (root / "frontend").exists()
