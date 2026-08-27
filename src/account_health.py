"""Task 2: TAM account-health summarization."""
from __future__ import annotations

from typing import Any

from src.config import settings
from src.data_loader import (
    get_account_tickets,
    get_dataset_reference_date,
    load_raw_tickets,
    resolve_account,
)
from src.exceptions import OutputValidationError
from src.llm_client import LLMClient, OfflineDeterministicEngine
from src.prompts import load_prompt
from src.schemas import AccountHealthBrief
from src.validation import verify_quote_exists


def _build_prompt(
    account: dict[str, Any],
    tickets: list[dict[str, Any]],
    reference_date: Any,
) -> str:
    return (
        "CUSTOMER ACCOUNT DATA (UNTRUSTED DATA)\n"
        f"{account}\n\n"
        f"DATASET REFERENCE DATE: {reference_date.isoformat()}\n"
        f"TICKET WINDOW: {settings.data.ticket_history_days} days\n\n"
        "TICKETS IN WINDOW\n"
        f"{tickets}\n\n"
        "Return only AccountHealthBrief JSON."
    )


def _verify_risk_evidence(
    brief: AccountHealthBrief,
    tickets: list[dict[str, Any]],
    escalation_notes: list[str],
) -> AccountHealthBrief:
    bodies = [str(ticket.get("body") or "") for ticket in tickets]
    for risk in brief.open_risks_and_flags:
        if risk.signal_source not in {"ticket", "escalation_note"}:
            continue

        if not verify_quote_exists(
            risk.quote_or_evidence,
            ticket_bodies=bodies,
            escalation_notes=escalation_notes,
        ):
            if settings.guardrails.strict_quote_verification:
                raise OutputValidationError(
                    f"Unverified evidence for risk: {risk.risk_title}"
                )

    return brief


def summarize_account_health(
    account_id: str,
    *,
    llm_client: LLMClient | None = None,
    offline_engine: OfflineDeterministicEngine | None = None,
) -> AccountHealthBrief:
    account = resolve_account(account_id)
    tickets, warnings = get_account_tickets(account_id)

    reference_date = get_dataset_reference_date(load_raw_tickets())
    if reference_date is None:
        raise OutputValidationError(
            "Dataset has no valid ticket reference date."
        )

    client = llm_client or llm_client_global
    engine = offline_engine or offline_engine_global

    if client.is_llm:
        raw = client.complete_json(
            load_prompt("account_health"),
            _build_prompt(account, tickets, reference_date),
            AccountHealthBrief.model_json_schema(),
        )
        brief = AccountHealthBrief.model_validate(raw)
    else:
        raw = engine.infer_account_health(
            account,
            tickets,
            warnings,
            reference_date,
        )
        brief = AccountHealthBrief.model_validate(raw)

    return _verify_risk_evidence(
        brief,
        tickets,
        list(account.get("escalation_notes") or []),
    )


llm_client_global = LLMClient()
offline_engine_global = OfflineDeterministicEngine()
