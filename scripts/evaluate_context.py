"""Measure offline symbol/source retrieval against a path-only baseline."""

import argparse
import json

from lazarus_sentinel.context import load_context, query_context

# Frozen questions and expected anchors. The baseline sees file names only.
QUESTIONS = (
    ("CLI dispatch", "backend/src/lazarus_sentinel/cli.py", "main", 85),
    ("Scan orchestration", "backend/src/lazarus_sentinel/service.py", "scan", 26),
    ("Graph validation", "backend/src/lazarus_sentinel/rules.py", "validate_graph", 26),
    (
        "Provider budget reservation",
        "backend/src/lazarus_sentinel/budget.py",
        "reserve",
        33,
    ),
    ("Viewer bundle loading", "frontend/src/validation.ts", "loadDemo", 48),
)

# PR #56 moved three definitions. Preserve the original answer key for replay.
ANCHOR_SETS = {
    "pr55": (85, 26, 26, 33, 48),
    "pr56": (105, 26, 26, 45, 55),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--anchor-set", choices=ANCHOR_SETS, default="pr56")
    args = parser.parse_args()
    manifest, graph = load_context(args.snapshot)
    cases = []
    for (question, path, symbol, _), line in zip(
        QUESTIONS, ANCHOR_SETS[args.anchor_set], strict=True
    ):
        baseline = [file.path for file in graph.files if file.path == path]
        cursor = None
        records = []
        context_bytes = 0
        while True:
            result = query_context(manifest, graph, "search", text=path, cursor=cursor)
            context_bytes += len(
                json.dumps(result, ensure_ascii=True, separators=(",", ":"))
            )
            records.extend(
                row
                for row in result["records"]
                if row["path"] == path
                and row["name"].rsplit(".", 1)[-1] == symbol
                and row["kind"] == "DEFINITION"
            )
            cursor = result["next_cursor"]
            if cursor is None:
                break
        correct = len(records) == 1 and records[0]["start_line"] == line
        cases.append(
            {
                "question": question,
                "baseline_correct_file": bool(baseline),
                "baseline_correct_symbol_span": False,
                "baseline_bytes": len(json.dumps(baseline, separators=(",", ":"))),
                "graph_correct_symbol_span": correct,
                "graph_context_bytes": context_bytes,
                "graph_answer": records[0] if correct else None,
                "unsupported_claims": sum(row["start_line"] != line for row in records),
            }
        )
    print(
        json.dumps(
            {
                "snapshot_id": manifest.snapshot_id,
                "anchor_set": args.anchor_set,
                "cases": cases,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
