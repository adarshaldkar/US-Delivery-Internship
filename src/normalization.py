"""Conservative text normalization and targeted PII masking."""
from __future__ import annotations

import re
from dataclasses import dataclass

from src.config import settings


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
JWT_RE = re.compile(
    r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")


@dataclass(frozen=True)
class NormalizedTicket:
    subject: str
    body: str
    combined_text: str
    truncated: bool
    pii_redacted: bool


def normalize_whitespace(value: str | None) -> str:
    if not value:
        return ""
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def normalize_company(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def mask_pii(value: str) -> tuple[str, bool]:
    if not value or not settings.guardrails.enable_pii_masking:
        return value, False

    changed = False
    masked = value
    for pattern, token in (
        (EMAIL_RE, "[REDACTED_EMAIL]"),
        (JWT_RE, "[REDACTED_TOKEN]"),
        (CARD_RE, "[REDACTED_CARD]"),
        (PHONE_RE, "[REDACTED_PHONE]"),
    ):
        updated = pattern.sub(token, masked)
        changed |= updated != masked
        masked = updated
    return masked, changed


def normalize_ticket(subject: str | None, body: str | None) -> NormalizedTicket:
    clean_subject = normalize_whitespace(subject)
    clean_body = normalize_whitespace(body)

    combined = clean_subject
    if clean_body:
        combined = f"{clean_subject}\n{clean_body}".strip()

    masked, redacted = mask_pii(combined)
    limit = settings.guardrails.max_ticket_length

    if len(masked) <= limit:
        return NormalizedTicket(
            clean_subject, clean_body, masked, False, redacted
        )

    subject_budget = min(len(clean_subject), max(1, limit // 3))
    body_budget = max(0, limit - subject_budget - 1)
    short_subject = clean_subject[:subject_budget]
    short_body = clean_body[:body_budget]

    return NormalizedTicket(
        short_subject,
        short_body,
        f"{short_subject}\n{short_body}".strip(),
        True,
        redacted,
    )
