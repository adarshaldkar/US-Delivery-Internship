"""
Unit tests for Task 2 TAM Account Health Summariser.
"""

import pytest
from src.account_health import summarize_account_health
from src.exceptions import AccountNotFoundError
from src.schemas import AccountHealthBrief


def test_summarize_valid_account():
    # ACC-3336 is Omni Consumer Products
    brief = summarize_account_health("ACC-3336")
    assert isinstance(brief, AccountHealthBrief)
    assert brief.company == "Omni Consumer Products"
    assert len(brief.executive_summary) > 50
    assert len(brief.recommended_talking_points) >= 1
    # Verify risk quotes have verbatim evidence
    for risk in brief.open_risks_and_flags:
        assert len(risk.quote_or_evidence) > 5


def test_summarize_invalid_account():
    with pytest.raises(AccountNotFoundError):
        summarize_account_health("ACC-99999")
