import os

os.environ["EXECUTION_MODE"] = "offline"

from src.account_health import summarize_account_health
from src.data_loader import load_raw_accounts
from src.triage import triage_ticket


def test_offline_triage():
    result = triage_ticket({
        "subject": "Unable to connect",
        "body": "The production connector is failing.",
    })
    assert result.product
    assert result.category in {
        "Bug", "Feature Request", "How-To", "Performance",
        "Billing", "Integration", "Onboarding", "Data Loss",
    }
    assert result.urgency in {"P1", "P2", "P3", "P4"}


def test_account_health_deterministic():
    account_id = load_raw_accounts()[0]["account_id"]
    first = summarize_account_health(account_id).model_dump()
    second = summarize_account_health(account_id).model_dump()
    assert first == second


def test_account_health_three_sections():
    account_id = load_raw_accounts()[0]["account_id"]
    result = summarize_account_health(account_id)
    assert result.executive_summary
    assert isinstance(result.open_risks_and_flags, list)
    assert result.recommended_talking_points
