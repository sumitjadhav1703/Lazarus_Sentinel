"""Static, bounded self index. Source files are parsed as data only."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from .intake import ScanError, _read, reject_symlink_components
from .models import stable_id

MAX_FILES = 500
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_INDEX_BYTES = 16 * 1024 * 1024
MAX_RECORDS = 30000
MANIFESTS = {
    ".python-version",
    "backend/pyproject.toml",
    "backend/uv.lock",
    "frontend/package.json",
    "frontend/package-lock.json",
    "scripts/context_typescript.cjs",
}
PATHS = ["backend/src", "scripts", "frontend/src", *sorted(MANIFESTS)]
PARSER = Path(__file__).resolve().parents[3] / "scripts" / "context_typescript.cjs"


def environment() -> dict[str, str]:
    """Prevent inherited provider keys, Node options and Git overrides in workers."""
    return {
        **{
            key: value
            for key, value in os.environ.items()
            if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TMP", "TEMP", "TMPDIR"}
        },
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_OPTIONAL_LOCKS": "0",
    }


def _run(
    args: list[str], *, root: Path, seconds: int, data: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            args,
            cwd=root,
            input=data,
            capture_output=True,
            timeout=seconds,
            env=environment(),
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise ScanError("CONTEXT_TIMEOUT") from None
    except OSError:
        raise ScanError("CONTEXT_TOOL_UNAVAILABLE") from None


def _language(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if path in MANIFESTS:
        return "manifest"
    if path.endswith(".py") and (
        parts[:2] == ("backend", "src") or (parts[:1] == ("scripts",) and len(parts) == 2)
    ):
        return "python"
    if parts[:2] == ("frontend", "src") and path.endswith((".ts", ".tsx")):
        return "typescript"
    return None


def _sources(root: Path) -> dict[str, tuple[str, bytes]]:
    reject_symlink_components(root)
    command = ["git", "-c", "core.fsmonitor=false", "-C", str(root)]
    top = _run([*command, "rev-parse", "--show-toplevel"], root=root, seconds=3)
    if top.returncode or Path(os.fsdecode(top.stdout.rstrip(b"\r\n"))) != root:
        raise ScanError("CONTEXT_NOT_REPOSITORY_ROOT")
    listing = _run([*command, "ls-files", "--stage", "-z", "--", *PATHS], root=root, seconds=4)
    if listing.returncode or len(listing.stdout) > MAX_INDEX_BYTES:
        raise ScanError("CONTEXT_GIT_FAILED")
    sources: dict[str, tuple[str, bytes]] = {}
    total = 0
    for entry in sorted(listing.stdout.split(b"\0")):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        try:
            path = raw_path.decode()
        except UnicodeDecodeError:
            raise ScanError("CONTEXT_INVALID_PATH") from None
        language = _language(path)
        if language is None:
            continue
        mode, _, stage = metadata.split()
        if mode not in {b"100644", b"100755"} or stage != b"0" or path in sources:
            raise ScanError("CONTEXT_UNSAFE_TRACKED_ENTRY")
        if len(sources) >= MAX_FILES:
            raise ScanError("CONTEXT_FILE_LIMIT")
        data = _read(root, path, MAX_FILE_BYTES)
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ScanError("CONTEXT_TOTAL_LIMIT")
        sources[path] = (language, data)
    if not sources:
        raise ScanError("CONTEXT_EMPTY_INDEX")
    return sources


def _python(path: str, text: str) -> dict[str, Any]:
    tree = ast.parse(text, filename=path)
    bindings: Counter[str] = Counter()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.arg)):
            bindings[node.arg if isinstance(node, ast.arg) else node.name] += 1
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bindings[node.id] += 1
        elif (
            isinstance(node, (ast.Attribute, ast.Subscript))
            and isinstance(node.ctx, (ast.Store, ast.Del))
            and isinstance(node.value, ast.Name)
        ):
            bindings[node.value.id] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bindings[alias.asname or alias.name.split(".")[0]] += 1
        elif isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and node.name:
            bindings[node.name] += 1
        elif isinstance(node, ast.MatchMapping) and node.rest:
            bindings[node.rest] += 1

    defs: list[dict[str, Any]] = []
    imports: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []

    def visit(node: ast.AST, owner: int | None, prefix: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            full = f"{prefix}.{node.name}" if prefix else node.name
            defs.append(
                {
                    "name": full,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno or node.lineno,
                    "owner": owner,
                    "callable": isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node in tree.body
                    and not node.decorator_list,
                }
            )
            index = len(defs) - 1
            for decorator in node.decorator_list:
                unknowns.append({"start_line": decorator.lineno, "kind": "IMPLICIT_DECORATOR_CALL"})
            body = set(node.body)
            for child in ast.iter_child_nodes(node):
                if child in body:
                    visit(child, index, full)
                else:
                    visit(child, owner, prefix)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                module = (
                    alias.name
                    if isinstance(node, ast.Import)
                    else ("." * node.level + (node.module or ""))
                )
                imports.append(
                    {
                        "module": module,
                        "name": None if isinstance(node, ast.Import) else alias.name,
                        "alias": alias.asname or alias.name.split(".")[0],
                        "bind": node in tree.body
                        and (
                            not isinstance(node, ast.Import)
                            or "." not in alias.name
                            or alias.asname is not None
                        ),
                        "line": node.lineno,
                        "end_line": node.end_lineno or node.lineno,
                        "owner": owner,
                    }
                )
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                name = f"{node.func.value.id}.{node.func.attr}"
            if name in {"__import__", "importlib.import_module"}:
                unknowns.append({"start_line": node.lineno, "kind": "DYNAMIC_IMPORT"})
            elif name in {"exec", "eval", "globals", "locals", "vars", "setattr", "delattr"}:
                unknowns.append({"start_line": node.lineno, "kind": "DYNAMIC_BINDING"})
            elif name:
                calls.append(
                    {
                        "name": name,
                        "line": node.lineno,
                        "end_line": node.end_lineno or node.lineno,
                        "owner": owner,
                    }
                )
            else:
                unknowns.append({"start_line": node.lineno, "kind": "UNRESOLVED_CALL"})
        for child in ast.iter_child_nodes(node):
            visit(child, owner, prefix)

    visit(tree, None, "")
    return {
        "definitions": defs,
        "imports": imports,
        "calls": calls,
        "bindings": dict(bindings),
        "unknowns": unknowns,
    }


def _module(path: str, language: str) -> str:
    if language == "python":
        relative = path.removeprefix("backend/src/").removesuffix(".py")
        return relative.removesuffix("/__init__").replace("/", ".")
    return path.removesuffix(".tsx").removesuffix(".ts")


def _import_module(path: str, language: str, specifier: str) -> list[str]:
    if language == "typescript":
        if not specifier.startswith(("./", "../")):
            return []
        parts = list(PurePosixPath(path).parts[:-1])
        for part in PurePosixPath(specifier).parts:
            if part == "..":
                if not parts:
                    return []
                parts.pop()
            else:
                parts.append(part)
        target = "/".join(parts)
        for suffix in (".js", ".jsx", ".ts", ".tsx"):
            target = target.removesuffix(suffix)
        return [target, f"{target}/index"]
    if not specifier.startswith("."):
        return [specifier]
    package = _module(path, language).split(".")
    if not path.endswith("/__init__.py"):
        package.pop()
    level = len(specifier) - len(specifier.lstrip("."))
    if level > len(package):
        return []
    return [
        ".".join(
            package[: len(package) - level + 1] + ([specifier[level:]] if specifier[level:] else [])
        )
    ]


def _build(root: Path) -> dict[str, Any]:
    sources = _sources(root)
    parsed: dict[str, Any] = {}
    ts: dict[str, str] = {}
    files: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    unknowns: list[dict[str, Any]] = []
    modules: dict[tuple[str, str], list[str]] = {}
    module_ids: dict[str, str] = {}
    definition_ids: dict[str, list[str]] = {}
    known_definitions: dict[tuple[str, str], list[str]] = {}
    exported_definitions: set[str] = set()
    entity_ordinals: Counter[tuple[str, str, str, int, int]] = Counter()
    relationship_ordinals: Counter[tuple[str, str, str, str, int, int]] = Counter()

    def entity(path: str, kind: str, name: str, start: int, end: int) -> str:
        key = (path, kind, name, start, end)
        identity = stable_id("context-entity", *key, entity_ordinals[key])
        entity_ordinals[key] += 1
        entities.append(
            {
                "id": identity,
                "kind": kind,
                "name": name,
                "path": path,
                "start_line": start,
                "end_line": end,
            }
        )
        return identity

    def relation(path: str, kind: str, source: str, target: str, start: int, end: int) -> None:
        key = (path, kind, source, target, start, end)
        identity = stable_id("context-relationship", *key, relationship_ordinals[key])
        relationship_ordinals[key] += 1
        relationships.append(
            {
                "id": identity,
                "kind": kind,
                "source": source,
                "target": target,
                "status": "OBSERVED",
                "path": path,
                "start_line": start,
                "end_line": end,
            }
        )

    def unknown(path: str, line: int, kind: str) -> None:
        unknowns.append({"path": path, "start_line": line, "kind": kind})

    for path, (language, data) in sorted(sources.items()):
        files.append(
            {"path": path, "sha256": hashlib.sha256(data).hexdigest(), "language": language}
        )
        count = max(1, len(data.splitlines()))
        if language == "typescript":
            count += data.count(b"\xe2\x80\xa8") + data.count(b"\xe2\x80\xa9")
        file = entity(path, "FILE", path, 1, count)
        if language == "manifest":
            coverage.append({"path": path, "capability": "inventory", "status": "OBSERVED"})
            continue
        module_name = _module(path, language)
        modules.setdefault((language, module_name), []).append(path)
        module = module_ids[path] = entity(path, "MODULE", module_name, 1, count)
        relation(path, "CONTAINS", file, module, 1, count)
        try:
            text = data.decode()
            if language == "python":
                parsed[path] = _python(path, text)
            else:
                ts[path] = text
        except (SyntaxError, UnicodeDecodeError, RecursionError):
            unknown(path, 1, "PARSE_ERROR")

    if ts:
        result = _run(
            ["node", "--max-old-space-size=256", str(PARSER)],
            root=root,
            seconds=12,
            data=json.dumps(ts).encode(),
        )
        if result.returncode or len(result.stdout) > MAX_INDEX_BYTES:
            raise ScanError("CONTEXT_TYPESCRIPT_FAILED")
        parsed.update(json.loads(result.stdout))

    for path, (language, _) in sorted(sources.items()):
        if language == "manifest":
            continue
        syntax = parsed.get(path)
        if syntax is None:
            if path in ts:
                unknown(path, 1, "PARSE_ERROR")
            for capability in ("definitions", "imports", "calls"):
                coverage.append({"path": path, "capability": capability, "status": "UNKNOWN"})
            continue
        ids = definition_ids[path] = []
        for definition in syntax["definitions"]:
            name = definition["name"]
            start, end = definition["start_line"], definition["end_line"]
            child = entity(path, "DEFINITION", name, start, end)
            owner = definition["owner"]
            relation(
                path,
                "CONTAINS",
                module_ids[path] if owner is None else ids[owner],
                child,
                start,
                end,
            )
            ids.append(child)
            if definition["callable"] and syntax["bindings"].get(name) == 1:
                known_definitions.setdefault((path, name), []).append(child)
                if language == "python" or definition.get("exported"):
                    exported_definitions.add(child)

    for path, syntax in sorted(parsed.items()):
        if syntax is None:
            continue
        language = sources[path][0]
        bindings = syntax["bindings"]
        imports: dict[str, tuple[str, str | None, int]] = {}
        ids = definition_ids[path]

        def owner_id(owner: int | None, *, _path: str = path, _ids: list[str] = ids) -> str:
            return module_ids[_path] if owner is None else _ids[owner]

        incomplete = {item["kind"] for item in syntax["unknowns"]}
        for item in syntax["unknowns"]:
            unknown(path, item["start_line"], item["kind"])
        for item in syntax["imports"]:
            possible = _import_module(path, language, item["module"])
            names = possible
            if item["name"] and language == "python":
                names = [*possible, *(f"{x}.{item['name']}" for x in possible)]
            candidates = [
                candidate for name in names for candidate in modules.get((language, name), [])
            ]
            if possible and language == "typescript" and item["module"].endswith((".ts", ".tsx")):
                suffix = PurePosixPath(item["module"]).suffix
                candidates = [
                    candidate for candidate in candidates if candidate == possible[0] + suffix
                ]
            if len(candidates) != 1 or item["name"] == "*":
                kind = (
                    "STAR_IMPORT"
                    if item["name"] == "*"
                    else "AMBIGUOUS_IMPORT"
                    if len(candidates) > 1
                    else "UNRESOLVED_OR_EXTERNAL_IMPORT"
                )
                unknown(path, item["line"], kind)
                incomplete.add(kind)
                continue
            target = candidates[0]
            relation(
                path,
                "IMPORTS",
                owner_id(item["owner"]),
                module_ids[target],
                item["line"],
                item["end_line"],
            )
            if item["bind"] and bindings.get(item["alias"]) == 1:
                imports[item["alias"]] = (target, item["name"], item["end_line"])
        for call in syntax["calls"]:
            name = call["name"]
            head, _, attribute = name.partition(".")
            targets: list[str] = []
            if bindings.get(head) == 1 and not incomplete.intersection(
                {"DYNAMIC_IMPORT", "DYNAMIC_BINDING", "STAR_IMPORT"}
            ):
                if head in imports:
                    target_path, imported, import_end = imports[head]
                    if bool(imported) != bool(attribute) and (
                        language != "python"
                        or call["owner"] is not None
                        or import_end < call["line"]
                    ):
                        targets = [
                            identity
                            for identity in known_definitions.get(
                                (target_path, imported or attribute), []
                            )
                            if identity in exported_definitions
                        ]
                elif not attribute:
                    targets = known_definitions.get((path, name), [])
                    if call["owner"] is None and not any(
                        definition["name"] == name and definition["end_line"] < call["line"]
                        for definition in syntax["definitions"]
                    ):
                        targets = []
            if len(targets) != 1:
                unknown(path, call["line"], "UNRESOLVED_CALL")
                incomplete.add("UNRESOLVED_CALL")
                continue
            relation(
                path, "CALLS", owner_id(call["owner"]), targets[0], call["line"], call["end_line"]
            )
        for capability in ("definitions", "imports", "calls"):
            affected = any(capability[:-1].upper() in reason for reason in incomplete)
            if capability == "calls" and "DYNAMIC_BINDING" in incomplete:
                affected = True
            status = "PARTIAL" if affected else "OBSERVED"
            coverage.append({"path": path, "capability": capability, "status": status})
        if len(entities) + len(relationships) + len(unknowns) > MAX_RECORDS:
            raise ScanError("CONTEXT_RECORD_LIMIT")

    return {
        "files": files,
        "entities": sorted(entities, key=lambda x: x["id"]),
        "relationships": sorted(relationships, key=lambda x: x["id"]),
        "coverage": coverage,
        "unknowns": sorted(
            {(x["path"], x["start_line"], x["kind"]): x for x in unknowns}.values(),
            key=lambda x: (x["path"], x["start_line"], x["kind"]),
        ),
    }


def build_index(root: Path) -> dict[str, Any]:
    root = root.absolute()
    result = _run(
        [sys.executable, "-I", "-m", "lazarus_sentinel.context_index", str(root)],
        root=root,
        seconds=30,
    )
    if result.returncode:
        code = result.stderr.decode(errors="replace").strip()
        raise ScanError(
            code if re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", code) else "CONTEXT_INDEX_FAILED"
        )
    if len(result.stdout) > MAX_INDEX_BYTES:
        raise ScanError("CONTEXT_INDEX_SIZE_LIMIT")
    index: dict[str, Any] = json.loads(result.stdout)
    return index


if __name__ == "__main__":
    try:
        payload = json.dumps(_build(Path(sys.argv[1])), separators=(",", ":")).encode()
        if len(payload) > MAX_INDEX_BYTES:
            raise ScanError("CONTEXT_INDEX_SIZE_LIMIT")
        sys.stdout.buffer.write(payload)
    except ScanError as error:
        print(error.code, file=sys.stderr)
        sys.exit(1)
