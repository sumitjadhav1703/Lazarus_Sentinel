import asyncio
import json
import sys

import pytest

from lazarus_sentinel import context, context_index
from lazarus_sentinel.cli import main


@pytest.fixture
def snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr(context, "WORKSPACE", tmp_path)
    monkeypatch.setattr(context.subprocess, "check_output", lambda *_args, **_kw: "a" * 40)
    rows = [
        {
            "id": f"entity-{n}",
            "kind": "DEFINITION",
            "name": f"item_{n}",
            "path": "scripts/test.py",
            "start_line": n + 1,
            "end_line": n + 1,
        }
        for n in range(110)
    ]
    monkeypatch.setattr(
        context_index,
        "build_index",
        lambda _: {
            "files": [{"path": "scripts/test.py", "sha256": "a" * 64, "language": "python"}],
            "entities": rows,
            "relationships": [
                {
                    "id": "edge-1",
                    "kind": "CALLS",
                    "source": "entity-0",
                    "target": "entity-1",
                    "status": "OBSERVED",
                    "path": "scripts/test.py",
                    "start_line": 1,
                    "end_line": 1,
                }
            ],
            "coverage": [{"path": "scripts/test.py", "capability": "calls", "status": "PARTIAL"}],
            "unknowns": [{"path": "scripts/test.py", "start_line": 2, "kind": "UNRESOLVED_CALL"}],
        },
    )
    return tmp_path, context.build_context()


def test_queries_and_cursors(snapshot, capsys):
    _, summary = snapshot
    identity = summary["snapshot_id"]
    command = [
        "context",
        "query",
        "--snapshot",
        identity,
        "--operation",
        "search",
        "--text",
        "item_",
    ]
    assert main(command) == 0
    first = json.loads(capsys.readouterr().out)
    assert len(first["records"]) == 100
    assert main(command + ["--cursor", first["next_cursor"]]) == 0
    second = json.loads(capsys.readouterr().out)
    assert len(second["records"]) == 10 and second["next_cursor"] is None
    assert main(command + ["--cursor", first["next_cursor"], "--text", "other"]) == 1
    assert json.loads(capsys.readouterr().out)["diagnostic_codes"] == ["CONTEXT_INVALID_CURSOR"]
    manifest, graph = context.load_context(identity)
    with pytest.raises(ValueError, match="CONTEXT_INVALID_QUERY"):
        context.query_context(manifest, graph, "search", text=" " * 200 + "item")
    with pytest.raises(ValueError, match="CONTEXT_UNKNOWN_ENTITY"):
        context.query_context(manifest, graph, "entity", "does-not-exist")


def test_hash_and_graph_references(snapshot):
    root, summary = snapshot
    manifest, graph = context.load_context(summary["snapshot_id"])
    broken = graph.model_dump()
    broken["relationships"][0]["target"] = "missing"
    with pytest.raises(ValueError, match="CONTEXT_INVALID_REFERENCES"):
        context.validated_graph(broken)
    (root / summary["artifact_dir"] / "graph.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="CONTEXT_HASH_MISMATCH"):
        context.load_context(manifest.snapshot_id)


def test_mcp_stdio_matches_cli(snapshot, monkeypatch, capfd):
    sdk = pytest.importorskip("mcp")
    stdio = pytest.importorskip("mcp.client.stdio")
    root, summary = snapshot
    identity = summary["snapshot_id"]
    assert (
        main(
            [
                "context",
                "query",
                "--snapshot",
                identity,
                "--operation",
                "entity",
                "--id",
                "entity-0",
            ]
        )
        == 0
    )
    expected = json.loads(capfd.readouterr().out)
    monkeypatch.undo()
    code = (
        "import sys; from pathlib import Path; "
        "from lazarus_sentinel import context; "
        "from lazarus_sentinel.context_mcp import serve; "
        "context.WORKSPACE=Path(sys.argv[1]); serve(sys.argv[2])"
    )

    async def smoke():
        params = sdk.StdioServerParameters(
            command=sys.executable, args=["-c", code, str(root), identity]
        )
        async with (
            stdio.stdio_client(params) as (reader, writer),
            sdk.ClientSession(reader, writer) as session,
        ):
            await session.initialize()
            response = await session.call_tool(
                "repository_context", {"operation": "entity", "entity_id": "entity-0"}
            )
            assert not response.isError
            assert context.canonical_bytes(response.structuredContent) == context.canonical_bytes(
                expected
            )

    asyncio.run(asyncio.wait_for(smoke(), timeout=15))
