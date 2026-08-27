"""Safe dataset loading, date anchoring and account/ticket joins."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.config import settings
from src.exceptions import AccountNotFoundError, DataLoadError, InvalidAccountIdError
from src.normalization import normalize_company


def parse_iso_datetime(value: str) -> datetime:
    """Parse ISO-8601 and normalize the value to UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Datetime must be a non-empty string.")

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    result = datetime.fromisoformat(text)
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)

    return result.astimezone(timezone.utc)


@lru_cache(maxsize=4)
def load_raw_tickets(path: Path | None = None) -> tuple[dict[str, Any], ...]:
    target = path or settings.paths.tickets_path
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Unable to load tickets: {target}") from exc

    if not isinstance(payload, list):
        raise DataLoadError("tickets.json must contain a JSON array.")

    return tuple(item for item in payload if isinstance(item, dict))


@lru_cache(maxsize=4)
def load_raw_accounts(path: Path | None = None) -> tuple[dict[str, Any], ...]:
    target = path or settings.paths.accounts_path
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Unable to load accounts: {target}") from exc

    if not isinstance(payload, list):
        raise DataLoadError("accounts.json must contain a JSON array.")

    return tuple(item for item in payload if isinstance(item, dict))


def get_dataset_reference_date(
    tickets: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> datetime | None:
    """Return the latest valid ticket created_at timestamp."""
    rows = tickets if tickets is not None else load_raw_tickets()
    dates: list[datetime] = []

    for ticket in rows:
        raw = ticket.get("created_at")
        if not raw:
            continue
        try:
            dates.append(parse_iso_datetime(raw))
        except ValueError:
            continue

    return max(dates) if dates else None


def get_account_by_id(
    account_id: str,
    accounts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(account_id, str) or not account_id.strip():
        raise InvalidAccountIdError("Account ID must be a non-empty string.")

    target = account_id.strip()
    rows = accounts if accounts is not None else load_raw_accounts()

    return next(
        (
            account for account in rows
            if str(account.get("account_id", "")).strip() == target
        ),
        None,
    )


def resolve_account(
    account_id: str,
    accounts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    account = get_account_by_id(account_id, accounts)
    if account is None:
        raise AccountNotFoundError(f"Account '{account_id.strip()}' was not found.")
    return account


def get_account_tickets(
    account_id: str,
    tickets: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    accounts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    days: int | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = list(tickets if tickets is not None else load_raw_tickets())
    account_rows = accounts if accounts is not None else load_raw_accounts()
    account = resolve_account(account_id, account_rows)

    target_id = str(account["account_id"]).strip()
    target_company = normalize_company(account.get("company"))
    history_days = days if days is not None else settings.data.ticket_history_days

    if history_days < 1:
        raise ValueError("Ticket history window must be at least one day.")

    if settings.data.reference_date_mode == "dataset_latest":
        reference_date = get_dataset_reference_date(rows)
    else:
        reference_date = datetime.now(timezone.utc)

    if reference_date is None:
        return [], ["NO_VALID_TICKET_CREATED_AT"]

    cutoff = reference_date - timedelta(days=history_days)
    matches: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen_ticket_ids: set[str] = set()

    for ticket in rows:
        ticket_id = str(ticket.get("ticket_id", "<unknown>"))
        raw_date = ticket.get("created_at")

        if not raw_date:
            warnings.append(f"MISSING_CREATED_AT:{ticket_id}")
            continue

        try:
            created = parse_iso_datetime(raw_date)
        except ValueError:
            warnings.append(f"INVALID_CREATED_AT:{ticket_id}")
            continue

        if created < cutoff:
            continue

        ticket_account_id = str(ticket.get("account_id", "")).strip()
        ticket_company = normalize_company(ticket.get("company"))

        exact_match = ticket_account_id == target_id
        fallback_match = (
            not exact_match
            and bool(target_company)
            and ticket_company == target_company
        )

        if not (exact_match or fallback_match):
            continue

        if exact_match and target_company and ticket_company and ticket_company != target_company:
            warnings.append(f"ACCOUNT_COMPANY_MISMATCH:{ticket_id}")

        if fallback_match:
            warnings.append(f"SYNTHETIC_ID_DISCREPANCY:{ticket_id}")

        if ticket_id != "<unknown>" and ticket_id in seen_ticket_ids:
            continue
        if ticket_id != "<unknown>":
            seen_ticket_ids.add(ticket_id)

        matches.append(ticket)

    matches.sort(
        key=lambda item: (
            parse_iso_datetime(item["created_at"]),
            str(item.get("ticket_id", "")),
        ),
        reverse=True,
    )

    return matches, sorted(set(warnings))


def discover_product_catalog(
    tickets: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    accounts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
) -> list[str]:
    ticket_rows = tickets if tickets is not None else load_raw_tickets()
    account_rows = accounts if accounts is not None else load_raw_accounts()
    values: set[str] = set()

    for ticket in ticket_rows:
        product = ticket.get("product")
        if isinstance(product, str) and product.strip():
            values.add(product.strip())

    for account in account_rows:
        for product in account.get("products") or []:
            if isinstance(product, str) and product.strip():
                values.add(product.strip())

    return sorted(values, key=str.casefold)
