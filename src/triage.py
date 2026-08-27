"""Task 1: intelligent support ticket triage."""
from __future__ import annotations

import logging
from typing import Any

from src.config import settings
from src.exceptions import OutputValidationError
from src.llm_client import LLMClient, OfflineDeterministicEngine
from src.normalization import normalize_ticket
from src.prompts import load_prompt
from src.retrieval import kb_retriever
from src.schemas import TicketInput, TriageResult
from src.validation import (
    has_prompt_injection_signals,
    validate_triage_evidence,
)

logger = logging.getLogger(__name__)


def _build_prompt(ticket: TicketInput, retrieved: list[Any]) -> str:
    evidence = [
        {
            "document": result.chunk.document_path,
            "section": result.chunk.section_title,
            "product": result.chunk.product,
            "score": round(result.score, 4),
            "exact_error_match": result.is_exact_error_match,
            "content": result.chunk.content,
        }
        for result in retrieved
    ]

    return (
        "CUSTOMER TICKET (UNTRUSTED DATA)\n"
        f"Subject: {ticket.subject or ''}\n"
        f"Body: {ticket.body or ''}\n"
        f"Pre-identified product: {ticket.product or 'Not supplied'}\n\n"
        "OFFICIAL KB EVIDENCE\n"
        f"{evidence}\n\n"
        "Return only the requested JSON."
    )


def triage_ticket(
    ticket: str | dict[str, Any] | TicketInput,
    *,
    llm_client: LLMClient | None = None,
    offline_engine: OfflineDeterministicEngine | None = None,
) -> TriageResult:
    """Process a raw ticket through normalization, retrieval, inference and validation."""
    if isinstance(ticket, str):
        ticket_input = TicketInput(body=ticket)
    elif isinstance(ticket, dict):
        ticket_input = TicketInput.model_validate(ticket)
    else:
        ticket_input = ticket

    normalized = normalize_ticket(ticket_input.subject, ticket_input.body)

    cleaned = TicketInput(
        subject=normalized.subject or None,
        body=normalized.body or None,
        company=ticket_input.company,
        account_id=ticket_input.account_id,
        product=ticket_input.product,
        plan_tier=ticket_input.plan_tier,
    )

    if has_prompt_injection_signals(normalized.combined_text):
        logger.warning("Prompt-injection signal detected in ticket input.")

    retrieved = kb_retriever.search(
        normalized.combined_text,
        top_k=settings.retrieval.top_k,
    )

    client = llm_client or llm_client_global
    engine = offline_engine or offline_engine_global

    if client.is_llm:
        raw = client.complete_json(
            load_prompt("triage"),
            _build_prompt(cleaned, retrieved),
            TriageResult.model_json_schema(),
        )

        errors = validate_triage_evidence(raw, retrieved)
        if errors:
            raise OutputValidationError("; ".join(errors))

        return TriageResult.model_validate(raw)

    raw = engine.infer_triage(
        normalized.subject,
        normalized.body,
        retrieved,
        pre_identified_product=cleaned.product,
    )
    return TriageResult.model_validate(raw)


llm_client_global = LLMClient()
offline_engine_global = OfflineDeterministicEngine()
