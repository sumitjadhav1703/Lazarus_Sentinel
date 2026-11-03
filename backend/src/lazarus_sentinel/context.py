"""Immutable local repository context and bounded provider-neutral queries."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Final, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .bundle import canonical_bytes, checked_uuid, digest, parse_json, read_bounded
from .intake import ScanError, reject_symlink_components
from .service import WORKSPACE

VERSION: Final = "repository-context/1.0"
GRAPH_LIMIT = 16 * 1024 * 1024
RESULT_LIMIT = 64 * 1024
OPERATIONS = ("overview", "search", "entity", "neighbors", "evidence")
Hex = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Text = Annotated[str, Field(min_length=1, max_length=512)]
Line = Annotated[int, Field(ge=1)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class File(Strict):
    path: Text
    sha256: Hex
    language: Text


class Span(Strict):
    path: Text
    start_line: Line
    end_line: Line


class Entity(Span):
    id: Text
    kind: Literal["FILE", "MODULE", "DEFINITION"]
    name: Text


class Relationship(Span):
    id: Text
    kind: Literal["CONTAINS", "IMPORTS", "CALLS"]
    source: Text
    target: Text
    status: Literal["OBSERVED", "INFERRED", "UNKNOWN", "UNRESOLVED"]


class Coverage(Strict):
    path: Text
    capability: Text
    status: Text


class Unknown(Strict):
    path: Text
    start_line: Line
    kind: Text


class ContextGraph(Strict):
    files: list[File] = Field(min_length=1, max_length=500)
    entities: list[Entity] = Field(max_length=25000)
    relationships: list[Relationship] = Field(max_length=100000)
    coverage: list[Coverage] = Field(max_length=5000)
    unknowns: list[Unknown] = Field(max_length=100000)


class Artifact(Strict):
    size: Annotated[int, Field(gt=0, le=GRAPH_LIMIT)]
    sha256: Hex


class Manifest(Strict):
    schema_version: Literal["repository-context/1.0"]
    snapshot_id: Text
    revision: Hex
    git_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40,64}$")]
    artifacts: dict[str, Artifact]


class QueryResult(Strict):
    schema_version: Literal["repository-context/1.0"]
    snapshot_id: Text
    revision: Hex
    operation: Literal["overview", "search", "entity", "neighbors", "evidence"]
    records: list[dict[str, Any]] = Field(max_length=100)
    coverage: list[Coverage]
    next_cursor: str | None


def validated_graph(raw: object) -> ContextGraph:
    try:
        graph = ContextGraph.model_validate(raw)
    except ValidationError:
        raise ValueError("CONTEXT_INVALID_GRAPH") from None
    files = {item.path for item in graph.files}
    ids = {item.id for item in graph.entities}
    all_ids = ids | {item.id for item in graph.relationships}
    rows: tuple[Entity | Relationship | Coverage | Unknown, ...] = (
        *graph.entities,
        *graph.relationships,
        *graph.coverage,
        *graph.unknowns,
    )
    if (
        len(files) != len(graph.files)
        or len(all_ids) != len(graph.entities) + len(graph.relationships)
        or any(
            PurePosixPath(p).as_posix() != p
            or PurePosixPath(p).is_absolute()
            or ".." in PurePosixPath(p).parts
            or ":" in p
            or "\\" in p
            or p == "."
            or any(ord(c) < 32 for c in p)
            for p in files
        )
        or any(item.path not in files for item in rows)
        or any(item.end_line < item.start_line for item in (*graph.entities, *graph.relationships))
        or any(edge.source not in ids or edge.target not in ids for edge in graph.relationships)
    ):
        raise ValueError("CONTEXT_INVALID_REFERENCES")
    return graph


def build_context() -> dict[str, Any]:
    from .context_index import build_index, environment

    try:
        graph = validated_graph(build_index(WORKSPACE))
    except ScanError as error:
        raise ValueError("CONTEXT_INDEX_FAILED") from error
    data = canonical_bytes(graph.model_dump(mode="json"))
    if len(data) > GRAPH_LIMIT:
        raise ValueError("CONTEXT_GRAPH_LIMIT")
    commit = subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", "rev-parse", "HEAD"],
        cwd=WORKSPACE,
        text=True,
        timeout=3,
        env=environment(),
    ).strip()
    snapshot_id = str(uuid4())
    schemas = canonical_bytes(
        {
            "graph": ContextGraph.model_json_schema(),
            "manifest": Manifest.model_json_schema(),
            "query_result": QueryResult.model_json_schema(),
        }
    )
    files = {"graph.json": data, "schema.json": schemas}
    manifest = Manifest(
        schema_version=VERSION,
        snapshot_id=snapshot_id,
        revision=digest(data),
        git_commit=commit,
        artifacts={
            name: Artifact(size=len(body), sha256=digest(body)) for name, body in files.items()
        },
    ).model_dump(mode="json")
    root = WORKSPACE / "artifacts" / "context"
    reject_symlink_components(root)
    root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".pending-", dir=root))
    try:
        for name, body in {**files, "manifest.json": canonical_bytes(manifest)}.items():
            with (stage / name).open("xb") as output:
                output.write(body)
        os.rename(stage, root / snapshot_id)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return {**manifest, "artifact_dir": f"artifacts/context/{snapshot_id}"}


def load_context(snapshot_id: str) -> tuple[Manifest, ContextGraph]:
    checked_uuid(snapshot_id)
    directory = WORKSPACE / "artifacts" / "context" / snapshot_id
    try:
        manifest = Manifest.model_validate(
            parse_json(read_bounded(directory / "manifest.json", 16384))
        )
        if manifest.snapshot_id != snapshot_id or set(manifest.artifacts) != {
            "graph.json",
            "schema.json",
        }:
            raise ValueError("CONTEXT_INVALID_MANIFEST")
        payloads = {}
        for name, artifact in manifest.artifacts.items():
            data = read_bounded(directory / name, GRAPH_LIMIT)
            if len(data) != artifact.size or digest(data) != artifact.sha256:
                raise ValueError("CONTEXT_HASH_MISMATCH")
            payloads[name] = data
        if digest(payloads["graph.json"]) != manifest.revision:
            raise ValueError("CONTEXT_HASH_MISMATCH")
        return manifest, validated_graph(parse_json(payloads["graph.json"]))
    except (
        OSError,
        ScanError,
        ValidationError,
        json.JSONDecodeError,
        UnicodeError,
        RecursionError,
    ):
        raise ValueError("CONTEXT_INVALID_SNAPSHOT") from None


def query_context(
    manifest: Manifest,
    graph: ContextGraph,
    operation: str,
    entity_id: str | None = None,
    text: str | None = None,
    cursor: str | None = None,
) -> dict[str, Any]:
    if (
        operation not in OPERATIONS
        or (operation == "search") != (text is not None)
        or (operation in {"entity", "neighbors", "evidence"}) != (entity_id is not None)
        or (text is not None and (len(text) > 160 or not text.strip()))
        or (entity_id is not None and len(entity_id) > 512)
    ):
        raise ValueError("CONTEXT_INVALID_QUERY")
    binding = digest(
        canonical_bytes([manifest.snapshot_id, manifest.revision, operation, entity_id, text])
    )
    offset = 0
    if cursor is not None:
        match = re.fullmatch(r"([0-9a-f]{64}):([1-9][0-9]{0,5})", cursor[:80])
        if not match or len(cursor) > 80 or match[1] != binding:
            raise ValueError("CONTEXT_INVALID_CURSOR")
        offset = int(match[2])
    files = {file.path: file.sha256 for file in graph.files}

    def evidence_record(item: Span) -> dict[str, Any]:
        return {**item.model_dump(mode="json"), "file_sha256": files[item.path]}

    coverage: list[dict[str, Any]] = []
    records: list[dict[str, Any]]
    if operation == "overview":
        records = [
            {
                "files": len(graph.files),
                "entities": len(graph.entities),
                "relationships": len(graph.relationships),
                "unknowns": len(graph.unknowns),
            },
            *({"coverage": row.model_dump(mode="json")} for row in graph.coverage),
            *({"unknown": row.model_dump(mode="json")} for row in graph.unknowns),
        ]
    elif operation == "search" and text is not None:
        term = text.strip().casefold()
        records = [
            evidence_record(item)
            for item in graph.entities
            if term in item.name.casefold() or term in item.path.casefold()
        ]
    else:
        entity = next((item for item in graph.entities if item.id == entity_id), None)
        if entity is None:
            raise ValueError("CONTEXT_UNKNOWN_ENTITY")
        coverage = [
            row.model_dump(mode="json") for row in graph.coverage if row.path == entity.path
        ]
        if operation == "neighbors":
            records = [
                evidence_record(edge)
                for edge in graph.relationships
                if entity.id in (edge.source, edge.target)
            ]
        elif operation == "evidence":
            records = [
                {
                    key: value
                    for key, value in evidence_record(entity).items()
                    if key in {"path", "start_line", "end_line", "file_sha256"}
                }
            ]
        else:
            records = [evidence_record(entity)]

    if offset and offset >= len(records):
        raise ValueError("CONTEXT_INVALID_CURSOR")
    response: dict[str, Any] = {
        "schema_version": VERSION,
        "snapshot_id": manifest.snapshot_id,
        "revision": manifest.revision,
        "operation": operation,
        "records": [],
        "coverage": coverage,
        "next_cursor": None,
    }
    for index, record in enumerate(records[offset : offset + 100], start=offset + 1):
        response["records"].append(record)
        response["next_cursor"] = f"{binding}:{index}" if index < len(records) else None
        if len(canonical_bytes(response)) > RESULT_LIMIT:
            response["records"].pop()
            if not response["records"]:
                raise ValueError("CONTEXT_RESULT_LIMIT")
            response["next_cursor"] = f"{binding}:{index - 1}"
            break
    if len(canonical_bytes(response)) > RESULT_LIMIT:
        raise ValueError("CONTEXT_RESULT_LIMIT")
    return response
