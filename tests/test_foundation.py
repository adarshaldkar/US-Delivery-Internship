import pytest

from src.data_loader import (
    discover_product_catalog,
    get_account_tickets,
    get_dataset_reference_date,
    load_raw_accounts,
    load_raw_tickets,
    parse_iso_datetime,
)
from src.exceptions import AccountNotFoundError
from src.retrieval import historical_ticket_retriever, kb_retriever
from src.schemas import TicketInput


def test_real_dataset_sizes():
    assert len(load_raw_tickets()) == 500
    assert len(load_raw_accounts()) == 50


def test_dynamic_reference_date():
    reference = get_dataset_reference_date()
    assert reference is not None
    assert reference.utcoffset() is not None


def test_dynamic_product_catalog():
    assert len(discover_product_catalog()) >= 5


def test_kb_discovery():
    documents = {chunk.document_path for chunk in kb_retriever.chunks}
    assert len(documents) == 9


def test_historical_retrieval():
    assert historical_ticket_retriever.search("connector timeout", top_k=3)


def test_exact_error_detection():
    results = kb_retriever.search("ERR_CONNECTION_TIMEOUT")
    assert any(result.is_exact_error_match for result in results)


def test_subject_only_ticket():
    assert TicketInput(subject="Login failure").subject == "Login failure"


def test_body_only_ticket():
    assert TicketInput(body="Dashboard is slow").body == "Dashboard is slow"


def test_empty_ticket_rejected():
    with pytest.raises(ValueError):
        TicketInput(subject=" ", body=" ")


def test_invalid_datetime():
    with pytest.raises(ValueError):
        parse_iso_datetime("not-a-date")


def test_unknown_account():
    with pytest.raises(AccountNotFoundError):
        get_account_tickets("ACC-DOES-NOT-EXIST")
