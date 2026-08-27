"""Post-inference structural and evidence guardrails."""
from __future__ import annotations

import json
import re
from typing import Any, Iterable

from src.exceptions import OutputValidationError


def normalize_evidence_text(value: str) -> str:
    value = value.replace("\u2018", "'").replace("\u2019", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", value.strip())


def verify_quote_exists(
    quote: str,
    *,
    ticket_bodies: Iterable[str] = (),
    escalation_notes: Iterable[str] = (),
) -> bool:
    if not isinstance(quote, str) or not quote.strip():
        return False

    candidate = normalize_evidence_text(quote)
    sources = list(ticket_bodies) + list(escalation_notes)

    return any(
        candidate in normalize_evidence_text(str(source))
        for source in sources
        if source
    )


def verify_kb_citation(
    document_path: str | None,
    retrieved_results: Iterable[Any],
) -> bool:
    if not document_path:
        return False

    expected = document_path.replace("\\", "/").lstrip("./")
    return any(
        str(getattr(getattr(item, "chunk", None), "document_path", ""))
        .replace("\\", "/")
        .lstrip("./")
        == expected
        for item in retrieved_results
    )


def verify_kb_excerpt(
    excerpt: str | None,
    retrieved_results: Iterable[Any],
) -> bool:
    if not excerpt:
        return False

    candidate = normalize_evidence_text(excerpt)
    return any(
        candidate in normalize_evidence_text(
            str(getattr(getattr(item, "chunk", None), "content", ""))
        )
        for item in retrieved_results
    )


def has_prompt_injection_signals(text: str | None) -> bool:
    if not text:
        return False

    patterns = (
        r"\bignore\s+(?:all\s+)?previous\s+instructions\b",
        r"\bdisregard\s+(?:the\s+)?system\s+prompt\b",
        r"\breveal\s+(?:the\s+)?system\s+prompt\b",
        r"\bshow\s+(?:your|the)\s+(?:system|developer)\s+prompt\b",
        r"\boverride\s+(?:the\s+)?instructions\b",
    )
    lowered = text.casefold()
    return any(re.search(pattern, lowered) for pattern in patterns)


def extract_json_from_llm_response(response: str) -> dict[str, Any]:
    if not isinstance(response, str) or not response.strip():
        raise OutputValidationError("LLM response is empty.")

    text = response.strip()
    candidates: list[str] = []

    fenced = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        flags=re.I | re.S,
    )
    if fenced:
        candidates.append(fenced.group(1))

    if text.startswith("{") and text.endswith("}"):
        candidates.append(text)

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    raise OutputValidationError("No valid JSON object found in model output.")


def validate_triage_evidence(
    result: dict[str, Any],
    retrieved_results: list[Any],
) -> list[str]:
    errors: list[str] = []

    if result.get("matched_kb_document") and not verify_kb_citation(
        result["matched_kb_document"], retrieved_results
    ):
        errors.append("KB document is not grounded in retrieved evidence.")

    if result.get("kb_resolution_steps") and not verify_kb_excerpt(
        result["kb_resolution_steps"], retrieved_results
    ):
        errors.append("KB resolution steps are not grounded in retrieved evidence.")

    return errors
