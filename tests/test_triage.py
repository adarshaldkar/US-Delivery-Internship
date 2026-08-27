"""
Unit tests for Task 1 Intelligent Ticket Triage Agent.
"""

import pytest
from src.schemas import TriageResult
from src.triage import triage_ticket


def test_triage_ticket_with_error_code():
    ticket = {
        "subject": "DataBridge Pro pipeline failing",
        "body": "Connector timeout with ERR_CONNECTION_TIMEOUT after 30s. Urgent assistance needed.",
        "company": "Initech"
    }
    result = triage_ticket(ticket)
    assert isinstance(result, TriageResult)
    assert result.product in ["DataBridge Pro", "CloudSync", "AnalyticsHub", "SecureVault", "WorkflowEngine"]
    assert result.urgency in ["P1", "P2", "P3", "P4"]
    assert result.is_known_issue is True
    assert result.matched_kb_document is not None


def test_triage_raw_string():
    raw_text = "How do I configure SSO single sign on in CloudSync with Okta?"
    result = triage_ticket(raw_text)
    assert isinstance(result, TriageResult)
    assert len(result.draft_response) > 20


def test_triage_empty_fails():
    with pytest.raises(ValueError):
        triage_ticket({"subject": "", "body": "   "})
