"""OpenAI adapter and deterministic offline fallback engine."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.config import settings
from src.exceptions import LLMUnavailableError
from src.retrieval import (
    HistoricalTicketResult,
    RetrievalResult,
    historical_ticket_retriever,
)
from src.validation import extract_json_from_llm_response

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin adapter around OpenAI structured output."""

    def __init__(self) -> None:
        self.config = settings.llm
        self.mode = self.config.execution_mode
        self._client: Any | None = None

        if self.mode == "auto":
            self.mode = "llm" if self._has_key() else "offline"

        if self.mode == "llm":
            self._initialize()

    def _has_key(self) -> bool:
        value = self.config.api_key.strip().casefold()
        return bool(value and value not in {"your_api_key_here", "your_key_here"})

    def _initialize(self) -> None:
        if not self._has_key():
            raise LLMUnavailableError(
                "EXECUTION_MODE=llm requires OPENAI_API_KEY."
            )

        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.config.api_key,
                timeout=self.config.request_timeout_seconds,
            )
        except Exception as exc:
            raise LLMUnavailableError(
                "Unable to initialize OpenAI client."
            ) from exc

    @property
    def is_llm(self) -> bool:
        return self.mode == "llm" and self._client is not None

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.is_llm:
            raise LLMUnavailableError("LLM mode is not active.")

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "structured_result",
                "strict": True,
                "schema": schema,
            },
        }

        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.temperature,
                seed=self.config.seed,
                response_format=response_format,
            )
        except Exception as exc:
            logger.warning("OpenAI request failed: %s", exc)
            raise LLMUnavailableError("OpenAI request failed.") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMUnavailableError("OpenAI returned an empty response.")

        return extract_json_from_llm_response(content)


class OfflineDeterministicEngine:
    """
    Credential-free deterministic engine.

    Ticket labels are obtained from weighted similarity over the supplied
    historical ticket corpus. No product/category/team lookup table is used.
    """

    @staticmethod
    def _weighted_vote(
        neighbours: list[HistoricalTicketResult],
        field: str,
    ) -> tuple[Any, float]:
        votes: dict[Any, float] = {}

        for neighbour in neighbours:
            value = neighbour.ticket.get(field)
            if value in (None, ""):
                continue

            weight = max(neighbour.similarity, 0.0) ** 2
            votes[value] = votes.get(value, 0.0) + weight

        if not votes:
            return None, 0.0

        winner, winner_weight = max(
            votes.items(),
            key=lambda pair: (pair[1], str(pair[0])),
        )
        total = sum(votes.values())
        confidence = winner_weight / total if total else 0.0
        return winner, confidence

    def infer_triage(
        self,
        ticket_subject: str,
        ticket_body: str,
        retrieval_results: list[RetrievalResult],
        pre_identified_product: str | None = None,
    ) -> dict[str, Any]:
        query = f"{ticket_subject}\n{ticket_body}".strip()
        neighbours = historical_ticket_retriever.search(query)

        if not neighbours:
            raise LLMUnavailableError(
                "Offline engine could not retrieve historical evidence."
            )

        product, product_conf = self._weighted_vote(neighbours, "product")
        area, area_conf = self._weighted_vote(neighbours, "product_area")
        category, category_conf = self._weighted_vote(neighbours, "category")
        urgency, urgency_conf = self._weighted_vote(neighbours, "urgency")

        product = pre_identified_product or product
        if not product or not area or not category or not urgency:
            raise LLMUnavailableError(
                "Offline historical evidence lacks required triage labels."
            )

        top_kb = retrieval_results[0] if retrieval_results else None
        kb_score = top_kb.score if top_kb else 0.0
        known = bool(
            top_kb and (
                top_kb.is_exact_error_match
                or kb_score >= settings.retrieval.min_confidence_threshold
            )
        )

        document = top_kb.chunk.document_path if known else None
        section = top_kb.chunk.section_title if known else None

        alternatives: list[str] = []
        for neighbour in neighbours[1:]:
            alt = neighbour.ticket.get("category")
            if alt and alt != category and alt not in alternatives:
                alternatives.append(str(alt))

        evidence_strength = sum(
            [product_conf, area_conf, category_conf, urgency_conf]
        ) / 4.0
        combined_confidence = (
            evidence_strength * 0.7 + kb_score * 0.3
        )

        resolution = None
        if known and top_kb:
            resolution = top_kb.chunk.content[:800]

        return {
            "product": product,
            "product_area": area,
            "category": category,
            "urgency": urgency,
            "urgency_reasoning": (
                "Classification is derived from weighted similarity to the "
                "supplied labeled historical-ticket corpus."
            ),
            "is_known_issue": known,
            "matched_kb_document": document,
            "matched_kb_section": section,
            "kb_resolution_steps": resolution,
            "recommended_team": "Technical Support (offline recommendation)",
            "draft_response": (
                "Hello,\n\n"
                "Thank you for contacting Technical Support. "
                f"Based on the available support evidence, this appears to be "
                f"a {category.lower()} affecting {product}. "
                "We will review the reported impact and follow up with the "
                "next actionable step.\n\n"
                "Best regards,\nTechnical Support"
            ),
            "secondary_topics": alternatives[:3],
            "confidence": round(
                max(0.0, min(1.0, combined_confidence)), 3
            ),
            "kb_retrieval_score": round(kb_score, 3) if top_kb else None,
        }

    @staticmethod
    def infer_account_health(
        account: dict[str, Any],
        tickets_90d: list[dict[str, Any]],
        data_quality_warnings: list[str],
        reference_date: datetime,
    ) -> dict[str, Any]:
        company = str(account.get("company") or "Unknown")
        tam = str(account.get("tam") or "Unassigned")
        plan = account.get("plan_tier")
        health = account.get("health_status")
        usage = account.get("usage_trend")
        arr = account.get("arr_usd")
        licensed = account.get("seats_licensed")
        active = account.get("seats_active")

        total_tickets = len(tickets_90d)
        p1_count = sum(ticket.get("urgency") == "P1" for ticket in tickets_90d)
        p2_count = sum(ticket.get("urgency") == "P2" for ticket in tickets_90d)

        utilization = None
        if isinstance(licensed, (int, float)) and licensed > 0:
            if isinstance(active, (int, float)):
                utilization = round(active / licensed * 100, 1)

        days_until_renewal = None
        renewal_date = account.get("renewal_date")
        if renewal_date:
            try:
                from src.data_loader import parse_iso_datetime
                renewal = parse_iso_datetime(str(renewal_date))
                days_until_renewal = (
                    renewal.date() - reference_date.date()
                ).days
            except ValueError:
                data_quality_warnings.append("INVALID_RENEWAL_DATE")

        sentence_parts = [
            (
                f"{company} is on the {plan or 'Unavailable'} plan with "
                f"{'unavailable' if arr is None else f'${arr:,}'} ARR."
            ),
            (
                f"The account health is {health or 'Unavailable'} and the "
                f"usage trend is {str(usage).lower() if usage else 'unavailable'}."
            ),
            (
                f"The selected 90-day window contains {total_tickets} support "
                f"tickets, including {p1_count} P1 and {p2_count} P2 incidents."
            ),
        ]

        if usage in {"Declining", "Inactive"}:
            sentence_parts.append(
                "The usage trajectory supports a proactive adoption review."
            )
        elif usage == "Increasing":
            sentence_parts.append(
                "The usage trajectory creates an opportunity for broader adoption."
            )
        else:
            sentence_parts.append(
                "The available account signals should be reviewed together by the TAM."
            )

        risks: list[dict[str, Any]] = []

        for note in account.get("escalation_notes") or []:
            evidence = str(note).strip()
            if evidence:
                risks.append({
                    "risk_title": "Account escalation note",
                    "severity": "Medium",
                    "signal_source": "escalation_note",
                    "quote_or_evidence": evidence,
                    "ticket_id": None,
                })

        for ticket in tickets_90d:
            if ticket.get("urgency") not in {"P1", "P2"}:
                continue
            if ticket.get("status") in {"Resolved", "Closed"}:
                continue

            evidence = str(ticket.get("body") or ticket.get("subject") or "").strip()
            if evidence:
                risks.append({
                    "risk_title": f"Open {ticket.get('urgency')} support incident",
                    "severity": (
                        "High" if ticket.get("urgency") == "P1" else "Medium"
                    ),
                    "signal_source": "ticket",
                    "quote_or_evidence": evidence[:500],
                    "ticket_id": ticket.get("ticket_id"),
                })

        talking_points: list[str] = []

        if days_until_renewal is not None:
            talking_points.append(
                "Review renewal timing against the account's technical priorities "
                f"({days_until_renewal} days from the dataset reference date)."
            )

        if usage in {"Declining", "Inactive"}:
            talking_points.append(
                f"Discuss the drivers behind the {str(usage).lower()} usage trend "
                "and agree on measurable adoption-recovery actions."
            )
        elif usage == "Increasing":
            talking_points.append(
                "Discuss opportunities for broader adoption across users, "
                "workflows, products, or integrations."
            )

        if p1_count:
            talking_points.append(
                f"Review the {p1_count} P1 incident(s), ownership, root-cause "
                "actions, and prevention plan."
            )

        if utilization is not None:
            talking_points.append(
                f"Review current seat utilization of {utilization}% and identify "
                "capacity or adoption opportunities."
            )

        if account.get("escalation_notes"):
            talking_points.append(
                "Close the loop on the stakeholder concerns in the account "
                "escalation notes and agree on owners for next actions."
            )

        if not talking_points:
            talking_points.append(
                "Review account objectives, recent support activity, and any "
                "missing information before the next TAM review."
            )

        return {
            "account_id": str(account.get("account_id") or ""),
            "company": company,
            "tam_name": tam,
            "plan_tier": plan,
            "arr_usd": arr,
            "health_status": health,
            "usage_trend": usage,
            "executive_summary": " ".join(sentence_parts),
            "open_risks_and_flags": risks,
            "recommended_talking_points": talking_points,
            "metrics_snapshot": {
                "reference_date": reference_date.isoformat(),
                "ticket_history_days": settings.data.ticket_history_days,
                "total_tickets_90d": total_tickets,
                "p1_tickets_90d": p1_count,
                "p2_tickets_90d": p2_count,
                "seat_utilization_pct": utilization,
                "days_until_renewal": days_until_renewal,
                "arr_usd": arr,
                "seats_licensed": licensed,
                "seats_active": active,
            },
            "data_quality_warnings": sorted(set(data_quality_warnings)),
        }


llm_client = LLMClient()
offline_engine = OfflineDeterministicEngine()
