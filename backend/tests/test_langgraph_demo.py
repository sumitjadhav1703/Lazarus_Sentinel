"""Exercise the opt-in graph with real artifact validation and no network."""

import importlib.util
import io
import json
import socket
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from test_explanations import committed_scan as _committed_scan

from lazarus_sentinel.cli import main


@pytest.fixture
def committed_scan(tmp_path, monkeypatch):
    return _committed_scan.__wrapped__(tmp_path, monkeypatch)


@pytest.mark.parametrize("fail_explanation", [False, True])
def test_langgraph_demo_preserves_provider_boundary(committed_scan, monkeypatch, fail_explanation):
    pytest.importorskip("langgraph.graph")
    root, scan_id = committed_scan
    script = Path(__file__).resolve().parents[2] / "scripts" / "prepare_demo.py"
    spec = importlib.util.spec_from_file_location("prepare_langgraph_demo", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    calls = []

    def reject_network(*_args, **_kwargs):
        pytest.fail("The offline workflow opened a socket")

    def cli(*args, expected=0):
        calls.append(args[0] if args[0] != "explain" else args[-1])
        if args[0] == "scan":
            assert args == ("scan", "--target", "fixture:fastapi-demo")
            assert expected == 2
            return {"scan_id": scan_id}
        if fail_explanation and args[-1] == "meta":
            raise module.DemoCommandError(["META_INVALID_RESPONSE"])
        with redirect_stdout(io.StringIO()) as output:
            assert main(args) == expected
        return json.loads(output.getvalue())

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    monkeypatch.setattr(module, "cli", cli)
    if fail_explanation:
        with pytest.raises(module.DemoCommandError) as caught:
            module.prepare(verify_only=True, workflow="langgraph", provider="meta")
        assert caught.value.codes == ["META_INVALID_RESPONSE"]
        assert len(calls) == 3
        assert calls[-1] == "meta"
        assert not (root / "artifacts" / "demo-bundles").exists()
    else:
        result = module.prepare(verify_only=True, workflow="langgraph")
        assert result["generation"] == "mock"
        assert calls[0] == "scan"
        assert len(calls) == 4
        assert calls[-2:] == ["mock", "demo"]
        assert (root / result["artifact_dir"] / "explanations.json").is_file()
    assert not (root / "artifacts" / "model-budget.sqlite3").exists()
    assert not (root / "frontend").exists()


def test_langgraph_cli_requires_verify_only():
    root = Path(__file__).resolve().parents[2]
    run = subprocess.run(
        [sys.executable, str(root / "scripts" / "prepare_demo.py"), "--workflow", "langgraph"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 2
    assert "--workflow langgraph requires --verify-only" in run.stderr
