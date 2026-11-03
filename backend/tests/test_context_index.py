import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

from lazarus_sentinel.context_index import MAX_FILE_BYTES, build_index
from lazarus_sentinel.intake import ScanError


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def write(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.fixture
def repo(tmp_path):
    root = tmp_path.resolve()
    git(root, "init", "--quiet")
    return root


@pytest.mark.skipif(
    shutil.which("node") is None
    or not (Path(__file__).resolve().parents[2] / "frontend/node_modules/typescript").is_dir(),
    reason="install locked frontend dependencies to exercise the TypeScript adapter",
)
def test_static_index_resolves_only_supported_relationships(repo):
    write(repo, "backend/src/pkg/a.py", b"def work():\n    return 1\n")
    observed = b"from .a import work\n\ndef run():\n    work()\n"
    write(repo, "backend/src/pkg/b.py", observed)
    write(repo, "backend/src/pkg/c.py", b"from .a import work\n\ndef run(work):\n    work()\n")
    write(repo, "backend/src/pkg/broken.py", b"def (:")
    write(repo, "frontend/src/a.ts", b"export function work() { return 1; }\n")
    write(repo, "frontend/src/b.tsx", b"import { work } from './a';\nfunction run() { work(); }")
    write(repo, "frontend/src/dynamic.ts", b"const x = import('./a');")
    write(repo, "backend/pyproject.toml", b'[project]\nname = "test"\n')
    write(repo, "frontend/src/.env", b"test-secret=not-indexed")
    write(repo, "artifacts/ignored.py", b"def hidden(): pass")
    git(repo, "add", ".")
    write(repo, "backend/src/pkg/untracked.py", b"def hidden(): pass")

    result = build_index(repo)
    assert build_index(repo) == result
    assert len(result["files"]) == 8
    files = {record["path"]: record for record in result["files"]}
    assert files["backend/src/pkg/b.py"]["sha256"] == hashlib.sha256(observed).hexdigest()
    entities = {record["id"]: record for record in result["entities"]}
    assert len(entities) == len(result["entities"])
    calls = [record for record in result["relationships"] if record["kind"] == "CALLS"]
    assert {record["path"] for record in calls} == {"backend/src/pkg/b.py", "frontend/src/b.tsx"}
    assert all(entities[record["target"]]["name"] == "work" for record in calls)
    assert all(entities[record["source"]]["name"] == "run" for record in calls)
    assert {"PARSE_ERROR", "UNRESOLVED_CALL", "DYNAMIC_IMPORT"} <= {
        item["kind"] for item in result["unknowns"]
    }
    assert {
        "path": "backend/src/pkg/broken.py",
        "capability": "calls",
        "status": "UNKNOWN",
    } in result["coverage"]


def test_worktree_alias_rejected(repo):
    source = write(repo, "backend/src/example.py", b"def work(): pass")
    git(repo, "add", "backend/src/example.py")
    outside = write(repo, "outside.py", b"def hidden(): pass")
    source.unlink()
    try:
        source.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    with pytest.raises(ScanError):
        build_index(repo)


def test_oversize_source_rejected(repo):
    write(repo, "backend/src/large.py", b"#" * (MAX_FILE_BYTES + 1))
    git(repo, "add", "backend/src/large.py")
    with pytest.raises(ScanError, match="INVALID_FILE"):
        build_index(repo)


@pytest.mark.skipif(
    shutil.which("node") is None
    or not (Path(__file__).resolve().parents[2] / "frontend/node_modules/typescript").is_dir(),
    reason="install locked frontend dependencies to exercise the TypeScript adapter",
)
def test_reassignments_and_signature_calls_are_conservative(repo):
    write(
        repo,
        "frontend/src/shadow.ts",
        b"""
function original() {}
function replacement() {}
original = replacement;
original();
""",
    )
    write(
        repo,
        "backend/src/pkg/side_effect.py",
        b"""
def helper():
    return 1
def decorator(fn):
    return fn
@decorator
def target(x=helper()):
    return x
class Model(helper()):
    pass
helper = target
helper()
""",
    )
    write(
        repo,
        "backend/src/pkg/defaults.py",
        b"""
def helper():
    return 1
def target(x=helper()):
    return x
class Model(helper()):
    pass
""",
    )
    git(repo, "add", ".")
    result = build_index(repo)
    calls = [edge for edge in result["relationships"] if edge["kind"] == "CALLS"]
    assert [
        (edge["path"], edge["start_line"])
        for edge in sorted(calls, key=lambda edge: edge["start_line"])
    ] == [("backend/src/pkg/defaults.py", 4), ("backend/src/pkg/defaults.py", 6)]
    assert {item["kind"] for item in result["unknowns"]} >= {
        "IMPLICIT_DECORATOR_CALL",
        "UNRESOLVED_CALL",
    }
    assert {"path": "frontend/src/shadow.ts", "capability": "calls", "status": "PARTIAL"} in result[
        "coverage"
    ]
