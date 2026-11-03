"""Public weakness references for a rule, optionally refreshed through Meta web search.

The search input is a fixed per-rule question. No source code, graph data or finding
text is ever sent, and only citations on allowlisted reference hosts are kept.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from pydantic import ValidationError

from . import intake
from .budget import INPUT_MICRO_USD_PER_TOKEN, OUTPUT_MICRO_USD_PER_TOKEN
from .bundle import canonical_bytes, digest
from .demo_models import WeaknessReferences
from .service import WORKSPACE

PROMPT_VERSION = "weakness-references-v1"
MODELS = {"mock": "deterministic-mock-v1", "meta": "muse-spark-1.3"}
ALLOWED_HOSTS = frozenset({"cwe.mitre.org", "owasp.org", "top10.owasp.org"})
# Reviewed static mapping; links verified 2026-11-03. The frontend mirrors this file.
RULE_REFERENCES: dict[str, dict[str, Any]] = {
    "LS-AUTH-001": {
        "question": (
            "Using web search, find the official MITRE CWE-862 Missing Authorization entry "
            "and the OWASP Top 10:2025 A01 Broken Access Control category. Cite only "
            "cwe.mitre.org and owasp.org pages. In at most three sentences, explain how "
            "missing authorization typically appears in web API endpoints."
        ),
        "references": [
            {
                "url": "https://cwe.mitre.org/data/definitions/862.html",
                "title": "CWE-862: Missing Authorization",
            },
            {
                "url": "https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/",
                "title": "OWASP Top 10:2025 A01 Broken Access Control",
            },
        ],
    }
}


def allowed_url(url: str) -> bool:
    parts = urlsplit(url)
    return (
        parts.scheme == "https"
        and parts.hostname in ALLOWED_HOSTS
        and parts.port is None
        and not parts.username
        and not parts.password
    )


def request_identity(rule_id: str, provider: str) -> dict[str, Any]:
    from .meta_provider import SEARCH_TOOLS

    return {
        "model": MODELS[provider],
        "prompt_version": PROMPT_VERSION,
        "provider": provider,
        "question": RULE_REFERENCES[rule_id]["question"],
        "rule_id": rule_id,
        "tools": SEARCH_TOOLS,
    }


def transport_payload(rule_id: str) -> bytes:
    from .meta_provider import SEARCH_OUTPUT_TOKENS, SEARCH_TOOLS

    return canonical_bytes(
        {
            "model": MODELS["meta"],
            "input": RULE_REFERENCES[rule_id]["question"],
            "tools": SEARCH_TOOLS,
            "max_output_tokens": SEARCH_OUTPUT_TOKENS,
            "reasoning": {"effort": "low"},
            "store": False,
            "stream": False,
        }
    )


def validate_references(record: WeaknessReferences | dict[str, Any]) -> WeaknessReferences:
    value = WeaknessReferences.model_validate(record)
    if value.rule_id not in RULE_REFERENCES:
        raise ValueError("UNKNOWN_RULE")
    if value.request_sha256 != digest(
        canonical_bytes(request_identity(value.rule_id, value.provider))
    ):
        raise ValueError("REFERENCES_REQUEST_MISMATCH")
    if not all(allowed_url(c.url) for c in value.citations):
        raise ValueError("UNTRUSTED_CITATION")
    return value


def lookup_references(rule_id: str, provider: str = "disabled") -> dict[str, Any]:
    if provider == "disabled":
        return {"status": "DISABLED", "provider": "disabled"}
    if provider not in MODELS:
        raise ValueError("INVALID_PROVIDER")
    if rule_id not in RULE_REFERENCES:
        raise ValueError("UNKNOWN_RULE")
    if provider == "mock":
        summary = (
            "Deterministic mock: the reviewed static references for this rule; no web search ran."
        )
        citations = RULE_REFERENCES[rule_id]["references"]
        usage = {"input_tokens": 0, "output_tokens": 0, "searches": 0}
    else:
        from .meta_provider import WEB_SEARCH_MICRO_USD, generate_search

        result, usage = generate_search(
            transport_payload(rule_id), WORKSPACE / "artifacts" / "agent-budget.sqlite3"
        )
        summary = result["text"]
        seen: set[str] = set()
        citations = []
        # Drop citations to any other host; keep the first title per URL.
        for citation in result["citations"]:
            if allowed_url(citation["url"]) and citation["url"] not in seen:
                seen.add(citation["url"])
                citations.append(citation)
        if not citations:
            raise ValueError("NO_TRUSTED_CITATIONS")
    try:
        record = WeaknessReferences.model_validate(
            {
                "references_version": "0.1.0",
                "reference_id": str(uuid4()),
                "rule_id": rule_id,
                "request_sha256": digest(canonical_bytes(request_identity(rule_id, provider))),
                "provider": provider,
                "model": MODELS[provider],
                "generation": "mock" if provider == "mock" else "live",
                "display_provenance": "recorded",
                "review_status": "UNREVIEWED",
                "created_at": datetime.now(UTC).isoformat(),
                "summary": summary,
                "citations": citations[:8],
                "usage": {
                    "calls": 1,
                    **usage,
                    "estimated_micro_usd": math.ceil(
                        usage["input_tokens"] * INPUT_MICRO_USD_PER_TOKEN
                        + usage["output_tokens"] * OUTPUT_MICRO_USD_PER_TOKEN
                    )
                    + (usage["searches"] * WEB_SEARCH_MICRO_USD if provider == "meta" else 0),
                },
            }
        )
    except ValidationError:
        raise ValueError("META_INVALID_RESPONSE") from None
    validate_references(record)
    data = canonical_bytes(record.model_dump(mode="json"))
    directory = WORKSPACE / "artifacts" / "references"
    intake.reject_symlink_components(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / f"{record.reference_id}.json"
    with path.open("xb") as stream:
        stream.write(data)
    return {
        "status": "RECORDED",
        "provider": provider,
        "reference_id": record.reference_id,
        "artifact_path": f"artifacts/references/{record.reference_id}.json",
        "rule_id": rule_id,
    }
