"""Explicit, bounded standard Meta transport. No retries, redirects, or error bodies."""

from __future__ import annotations

import http.client
import multiprocessing
import os
import re
import sys
import time
from multiprocessing.connection import Connection
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    if sys.platform == "win32":
        from multiprocessing.context import SpawnContext as TransportContext
    else:
        from multiprocessing.context import ForkContext as TransportContext

from .budget import Budget
from .bundle import canonical_bytes, parse_json

DEADLINE_SECONDS = 20.0
MAX_RESPONSE_BYTES = 32768
# Provider-side shape constraint. Local validation still enforces length and citation rules.
RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "evidence_explanation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "why_it_matters": {"type": "string"},
                "limitations": {"type": "array", "items": {"type": "string"}},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary", "why_it_matters", "limitations", "evidence_ids"],
            "additionalProperties": False,
        },
    },
}


CHAT_PATH = "/v1/chat/completions"
RESPONSES_PATH = "/v1/responses"


def _transport(payload: bytes, key: str, path: str = CHAT_PATH) -> dict[str, Any]:
    if path not in (CHAT_PATH, RESPONSES_PATH):
        raise ValueError("META_TRANSPORT_FAILED")
    connection = http.client.HTTPSConnection("api.meta.ai", timeout=DEADLINE_SECONDS)
    try:
        connection.request(
            "POST",
            path,
            body=payload,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError("META_TRANSPORT_FAILED")
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError("META_RESPONSE_LIMIT")
        parsed = parse_json(data)
        if not isinstance(parsed, dict):
            raise TypeError("META_INVALID_RESPONSE")
        return parsed
    finally:
        connection.close()


def _child(pipe: Connection, payload: bytes, key: str, path: str = CHAT_PATH) -> None:
    try:
        result = canonical_bytes(_transport(payload, key, path))
        if len(result) > MAX_RESPONSE_BYTES:
            raise ValueError("META_RESPONSE_LIMIT")
        pipe.send_bytes(b"O" + result)
    except BaseException:  # noqa: BLE001 - child boundary must redact all failures
        # Provider exceptions may carry credentials, prompts or remote bodies.
        pipe.send_bytes(b"E")
    finally:
        pipe.close()


def bounded_transport(payload: bytes, key: str, path: str = CHAT_PATH) -> dict[str, Any]:
    context = cast(
        "TransportContext",
        multiprocessing.get_context("spawn" if sys.platform == "win32" else "fork"),
    )
    reader, writer = context.Pipe(duplex=False)
    # The default path keeps the original child call shape.
    args = (writer, payload, key) if path == CHAT_PATH else (writer, payload, key, path)
    process = context.Process(target=_child, args=args, daemon=True)
    deadline = time.monotonic() + DEADLINE_SECONDS
    process.start()
    writer.close()
    try:
        if not reader.poll(max(0, deadline - time.monotonic())):
            raise ValueError("META_DEADLINE_EXCEEDED")
        try:
            data = reader.recv_bytes(MAX_RESPONSE_BYTES + 1)
        except (EOFError, OSError):
            raise ValueError("META_TRANSPORT_FAILED") from None
        if not data.startswith(b"O"):
            raise ValueError("META_TRANSPORT_FAILED")
        result = parse_json(data[1:])
        if not isinstance(result, dict):
            raise TypeError("META_INVALID_RESPONSE")
        return result
    finally:
        reader.close()
        if process.is_alive():
            process.kill()
        process.join(timeout=1)
        process.close()


def generate(payload: bytes, ledger_path: Path) -> dict[str, Any]:
    key = os.environ.get("MODEL_API_KEY")
    if not key:
        raise ValueError("META_KEY_MISSING")
    request = parse_json(payload)
    if (
        len(payload) > 16384
        or request.get("model") != "muse-spark-1.3"
        or request.get("max_completion_tokens") != 1024
        or request.get("reasoning_effort") != "minimal"
        or request.get("response_format") != RESPONSE_FORMAT
        or request.get("stream") is not False
        or set(request)
        != {
            "model",
            "messages",
            "max_completion_tokens",
            "reasoning_effort",
            "response_format",
            "stream",
        }
    ):
        raise ValueError("INVALID_META_REQUEST")
    budget = Budget(ledger_path)
    attempt = budget.reserve(len(payload))
    result = bounded_transport(payload, key)
    usage = result.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("UNVERIFIABLE_USAGE")  # noqa: TRY004 - allowlisted CLI diagnostic
    input_tokens, output_tokens = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if type(input_tokens) is not int or type(output_tokens) is not int:
        raise ValueError("UNVERIFIABLE_USAGE")
    if "total_tokens" in usage and (
        type(usage["total_tokens"]) is not int
        or usage["total_tokens"] != input_tokens + output_tokens
    ):
        raise ValueError("UNVERIFIABLE_USAGE")
    budget.settle(attempt, input_tokens, output_tokens)
    choices = result.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("META_INVALID_RESPONSE")
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("META_INVALID_RESPONSE")  # noqa: TRY004 - allowlisted CLI diagnostic
    if (
        choice.get("finish_reason") == "tool_calls"
        or message.get("tool_calls")
        or message.get("function_call")
    ):
        raise ValueError("META_UNEXPECTED_TOOLS")
    content = message.get("content")
    if choice.get("finish_reason") == "length" or not isinstance(content, str):
        raise ValueError("META_INVALID_RESPONSE")
    try:
        encoded = content.encode()
        if len(encoded) > MAX_RESPONSE_BYTES:
            raise ValueError("META_INVALID_RESPONSE")
        response = parse_json(encoded)
    except (ValueError, RecursionError):
        raise ValueError("META_INVALID_RESPONSE") from None
    if not isinstance(response, dict):
        raise ValueError("META_INVALID_RESPONSE")  # noqa: TRY004 - allowlisted CLI diagnostic
    return response


# Investigation turns use a separate ledger so the recorded explanation cap stays untouched.
AGENT_MAX_REQUEST_BYTES = 32768
AGENT_OUTPUT_TOKENS = 2048
AGENT_MAX_ATTEMPTS = 20
AGENT_MAX_BUDGET = 1_000_000


def generate_turn(
    payload: bytes, ledger_path: Path, tools: list[dict[str, Any]]
) -> tuple[dict[str, str], dict[str, int]]:
    """One bounded tool-calling turn. Returns exactly one validated tool call and usage."""
    key = os.environ.get("MODEL_API_KEY")
    if not key:
        raise ValueError("META_KEY_MISSING")
    request = parse_json(payload)
    if (
        len(payload) > AGENT_MAX_REQUEST_BYTES
        or request.get("model") != "muse-spark-1.3"
        or request.get("max_completion_tokens") != AGENT_OUTPUT_TOKENS
        or request.get("reasoning_effort") != "low"
        or request.get("tools") != tools
        or request.get("parallel_tool_calls") is not False
        or request.get("stream") is not False
        or set(request)
        != {
            "model",
            "messages",
            "tools",
            "parallel_tool_calls",
            "max_completion_tokens",
            "reasoning_effort",
            "stream",
        }
    ):
        raise ValueError("INVALID_META_REQUEST")
    budget = Budget(
        ledger_path,
        max_attempts=AGENT_MAX_ATTEMPTS,
        max_budget=AGENT_MAX_BUDGET,
        output_tokens=AGENT_OUTPUT_TOKENS,
        max_request_bytes=AGENT_MAX_REQUEST_BYTES,
    )
    attempt = budget.reserve(len(payload))
    result = bounded_transport(payload, key)
    usage = result.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("UNVERIFIABLE_USAGE")  # noqa: TRY004 - allowlisted CLI diagnostic
    input_tokens, output_tokens = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if type(input_tokens) is not int or type(output_tokens) is not int:
        raise ValueError("UNVERIFIABLE_USAGE")
    if "total_tokens" in usage and (
        type(usage["total_tokens"]) is not int
        or usage["total_tokens"] != input_tokens + output_tokens
    ):
        raise ValueError("UNVERIFIABLE_USAGE")
    budget.settle(attempt, input_tokens, output_tokens)
    choices = result.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("META_INVALID_RESPONSE")
    choice = choices[0]
    message = choice.get("message")
    if not isinstance(message, dict) or choice.get("finish_reason") == "length":
        raise ValueError("META_INVALID_RESPONSE")
    calls = message.get("tool_calls")
    # Free text instead of a tool call ends the run; the final answer must be submit_investigation.
    if not isinstance(calls, list) or not calls:
        raise ValueError("META_NO_TOOL_CALL")
    if len(calls) != 1 or not isinstance(calls[0], dict):
        raise ValueError("META_INVALID_RESPONSE")
    call = calls[0]
    function = call.get("function")
    if (
        call.get("type") != "function"
        or not isinstance(call.get("id"), str)
        or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", call["id"])
        or not isinstance(function, dict)
        or not isinstance(function.get("name"), str)
        or not isinstance(function.get("arguments"), str)
        or len(function["arguments"].encode()) > 8192
    ):
        raise ValueError("META_INVALID_RESPONSE")
    return (
        {"id": call["id"], "name": function["name"], "arguments": function["arguments"]},
        {"input_tokens": input_tokens, "output_tokens": output_tokens},
    )


# Verified 2026-11-03: https://dev.meta.ai/docs/pricing-rate-limits lists web_search at
# USD 2.50 per 1,000 queries on top of token cost. Integer micro-USD.
WEB_SEARCH_MICRO_USD = 2500
SEARCH_OUTPUT_TOKENS = 1024
SEARCH_MAX_QUERIES = 3
SEARCH_TOOLS = [{"type": "web_search", "search_context_size": "low"}]


def _search_queries(item: object) -> int:
    """Count recognized search queries or leave ambiguous usage unsettled."""
    if not isinstance(item, dict) or item.get("type") != "web_search_call":
        return 0
    action = item.get("action")
    if isinstance(action, dict) and action.get("type") == "search":
        queries = action.get("queries")
        if (
            isinstance(queries, list)
            and queries
            and all(isinstance(query, str) and query.strip() for query in queries)
        ):
            return len(queries)
        legacy_query = action.get("query")
        if "queries" not in action and isinstance(legacy_query, str) and legacy_query.strip():
            return 1
    raise ValueError("META_SEARCH_QUERY_SHAPE")


def generate_search(payload: bytes, ledger_path: Path) -> tuple[dict[str, Any], dict[str, int]]:
    """One bounded Responses call with Meta's built-in web search. The input carries no code."""
    key = os.environ.get("MODEL_API_KEY")
    if not key:
        raise ValueError("META_KEY_MISSING")
    request = parse_json(payload)
    if (
        len(payload) > 4096
        or request.get("model") != "muse-spark-1.3"
        or not isinstance(request.get("input"), str)
        or request.get("tools") != SEARCH_TOOLS
        or request.get("max_output_tokens") != SEARCH_OUTPUT_TOKENS
        or request.get("reasoning") != {"effort": "low"}
        or request.get("store") is not False
        or request.get("stream") is not False
        or set(request)
        != {"model", "input", "tools", "max_output_tokens", "reasoning", "store", "stream"}
    ):
        raise ValueError("INVALID_META_REQUEST")
    budget = Budget(
        ledger_path,
        max_attempts=AGENT_MAX_ATTEMPTS,
        max_budget=AGENT_MAX_BUDGET,
        output_tokens=AGENT_OUTPUT_TOKENS,
        max_request_bytes=AGENT_MAX_REQUEST_BYTES,
    )
    attempt = budget.reserve(len(payload))
    result = bounded_transport(payload, key, RESPONSES_PATH)
    usage, output = result.get("usage"), result.get("output")
    if not isinstance(output, list):
        raise ValueError("META_SEARCH_OUTPUT_SHAPE")  # noqa: TRY004 - safe CLI diagnostic
    if not isinstance(usage, dict):
        raise ValueError("META_SEARCH_TOKEN_USAGE")  # noqa: TRY004 - safe CLI diagnostic
    input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
    if type(input_tokens) is not int or type(output_tokens) is not int:
        raise ValueError("META_SEARCH_TOKEN_USAGE")
    if "total_tokens" in usage and (
        type(usage["total_tokens"]) is not int
        or usage["total_tokens"] != input_tokens + output_tokens
    ):
        raise ValueError("META_SEARCH_TOKEN_USAGE")
    searches = sum(_search_queries(i) for i in output)
    # Settle before validating content so every billed search is recorded.
    try:
        budget.settle(attempt, input_tokens, output_tokens, searches * WEB_SEARCH_MICRO_USD)
    except ValueError as exc:
        if str(exc) != "UNVERIFIABLE_USAGE":
            raise
        raise ValueError("META_SEARCH_SETTLEMENT_REJECTED") from None
    if result.get("status") != "completed" or searches > SEARCH_MAX_QUERIES:
        raise ValueError("META_INVALID_RESPONSE")
    texts: list[str] = []
    citations: list[dict[str, str]] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            raise ValueError("META_INVALID_RESPONSE")  # noqa: TRY004 - allowlisted CLI diagnostic
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "output_text":
                continue
            text, annotations = block.get("text"), block.get("annotations", [])
            if not isinstance(text, str) or not isinstance(annotations, list):
                raise ValueError("META_INVALID_RESPONSE")  # noqa: TRY004 - allowlisted CLI diagnostic
            texts.append(text)
            for note in annotations:
                if isinstance(note, dict) and note.get("type") == "url_citation":
                    url, title = note.get("url"), note.get("title")
                    if not isinstance(url, str) or not isinstance(title, str):
                        raise ValueError("META_INVALID_RESPONSE")
                    citations.append({"url": url, "title": title})
    return (
        {"text": "\n".join(texts).strip(), "citations": citations},
        {"input_tokens": input_tokens, "output_tokens": output_tokens, "searches": searches},
    )
