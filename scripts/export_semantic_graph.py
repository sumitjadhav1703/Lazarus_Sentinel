"""Export a new canonical graph for the controlled DATA fixture."""

import sys
from pathlib import Path
from uuid import uuid4

import semantic_spike as spike
from assess_data import load_policy, validate_evidence
from lazarus_sentinel.bundle import canonical_bytes
from lazarus_sentinel.semantic_graph import project_data, validate_data_graph

OUTPUT_ROOT = spike.ROOT / "artifacts" / "semantic-graphs"


def export_data_graph() -> Path:
    policy = spike.bounded_read(spike.CORPUS / "data_policy.json")
    load_policy(policy)
    sources = {}
    observations = {}
    for case in spike.CASE_IDS:
        source_path = spike.CORPUS / f"{case}.py"
        path = source_path.relative_to(spike.ROOT).as_posix()
        source = spike.bounded_read(source_path)
        observed = spike.analyze_source(source, file_path=path)
        validate_evidence(source, observed)
        sources[path] = source
        observations[path] = observed
    graph = project_data(policy, sources, observations)
    validate_data_graph(graph, policy, sources, observations)
    data = canonical_bytes(graph)
    if len(data) > spike.MAX_ARTIFACT:
        raise spike.ExperimentError("ARTIFACT_BYTES_EXCEEDED")
    run = OUTPUT_ROOT / str(uuid4())
    spike.reject_aliases(run)
    run.mkdir(parents=True, exist_ok=False)
    pending = run / "graph.tmp"
    with pending.open("xb") as stream:
        stream.write(data)
    output = run / "graph.json"
    pending.rename(output)
    return output


if __name__ == "__main__":
    if sys.argv[1:]:
        raise SystemExit("The fixed semantic exporter takes no arguments.")
    try:
        print(export_data_graph())
    except (OSError, ValueError, spike.ExperimentError):
        raise SystemExit("SEMANTIC_GRAPH_EXPORT_FAILED") from None
