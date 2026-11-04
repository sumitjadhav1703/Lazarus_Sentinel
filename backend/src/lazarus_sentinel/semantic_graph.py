"""Canonical graph projection for the fixed DATA policy."""

import re
from typing import Any

from .bundle import canonical_bytes, digest
from .models import Edge, Evidence, Node, stable_id

SCHEMA = "semantic-graph/0.2.0"
PROFILE = "controlled-data"
RULE = "LS-DATA-001"


def project_data(
    policy: bytes, sources: dict[str, bytes], assessments: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Project a policy and fresh observations already validated by the DATA assessor."""
    if not sources or sources.keys() != assessments.keys():
        raise ValueError("INVALID_DATA_CASES")
    hashes = {path: digest(source) for path, source in sorted(sources.items())}
    policy_hash = digest(policy)
    revision = digest(canonical_bytes([SCHEMA, policy_hash, hashes]))
    nodes: list[Node] = []
    edges: list[Edge] = []
    evidence: list[Evidence] = []
    findings = []
    coverage = []
    for path, source in sorted(sources.items()):
        result = assessments[path]
        status = result["status"]
        if result["source_sha256"] != hashes[path]:
            raise ValueError("INVALID_DATA_SOURCE")
        if status not in {"FLOW_OBSERVED", "NO_FLOW_IN_SUBSET", "UNKNOWN"}:
            raise ValueError("INVALID_DATA_STATUS")
        coverage.append({"path": path, "status": status})
        if status != "FLOW_OBSERVED":
            continue
        spans = result["path"]
        kinds = [span["kind"] for span in spans]
        if (
            len(kinds) < 2
            or kinds[0] != "parameter"
            or kinds[-1] != "marker_argument"
            or any(kind != "copy_assignment" for kind in kinds[1:-1])
        ):
            raise ValueError("INVALID_DATA_PATH")
        # Keep raw line endings so excerpt hashes bind the captured bytes.
        lines = re.split(rb"(?<=\n)|(?<=\r)(?!\n)", source)
        path_nodes: list[str] = []
        path_edges = []
        path_evidence: list[str] = []
        previous_end = (0, 0)
        for span in spans:
            start = (span["start_line"], span["start_col"])
            end = (span["end_line"], span["end_col"])
            if not (
                previous_end <= start < end
                and 1 <= start[0] <= end[0] <= len(lines)
                and 0 <= start[1] < len(lines[start[0] - 1])
                and 0 < end[1] <= len(lines[end[0] - 1])
            ):
                raise ValueError("INVALID_DATA_SPAN")
            previous_end = end
            excerpt = b"".join(lines[start[0] - 1 : end[0]])
            tail = sum(map(len, lines[start[0] - 1 : end[0] - 1])) + end[1]
            if digest(excerpt[start[1] : tail]) != span["sha256"]:
                raise ValueError("INVALID_DATA_SPAN")
            kind = span["kind"]
            ev_id = stable_id("evidence", revision, path, start, end)
            node_id = stable_id("node", revision, path, kind, start, end)
            evidence.append(
                Evidence(
                    id=ev_id,
                    repository_revision=revision,
                    file_path=path,
                    start_line=start[0],
                    end_line=end[0],
                    excerpt_hash="sha256:" + digest(excerpt),
                    analyzer_name="bounded_ast_provenance",
                    rule_or_query_id=RULE,
                    evidence_kind=kind,
                )
            )
            nodes.append(
                Node(
                    id=node_id,
                    type=kind.upper(),
                    layer="CODE",
                    name=kind,
                    evidence_ids=[ev_id],
                    properties={"start_col": start[1], "end_col": end[1]},
                )
            )
            if path_nodes:
                edge_id = stable_id("edge", revision, path_nodes[-1], node_id, "FLOWS_TO")
                edges.append(
                    Edge(
                        id=edge_id,
                        source=path_nodes[-1],
                        target=node_id,
                        type="FLOWS_TO",
                        evidence_ids=[path_evidence[-1], ev_id],
                    )
                )
                path_edges.append(edge_id)
            path_nodes.append(node_id)
            path_evidence.append(ev_id)
        findings.append(
            {
                "id": stable_id("finding", revision, path, RULE),
                "rule_id": RULE,
                "verification_status": "CANDIDATE",
                "confidence": "LOW",
                "path_node_ids": path_nodes,
                "path_edge_ids": path_edges,
                "evidence_ids": path_evidence,
            }
        )
    return {
        "schema_version": SCHEMA,
        "profile": PROFILE,
        "revision": revision,
        "policy_sha256": policy_hash,
        "source_sha256": hashes,
        "nodes": [item.model_dump(mode="json") for item in nodes],
        "edges": [item.model_dump(mode="json") for item in edges],
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "findings": findings,
        "coverage": coverage,
    }


def validate_data_graph(
    graph: dict[str, Any],
    policy: bytes,
    sources: dict[str, bytes],
    assessments: dict[str, dict[str, Any]],
) -> None:
    """Compare against the canonical projection of fresh, validated observations."""
    if canonical_bytes(graph) != canonical_bytes(project_data(policy, sources, assessments)):
        raise ValueError("INVALID_CANONICAL_DATA_GRAPH")
