"""Lightweight FastAPI endpoints."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.account_health import summarize_account_health
from src.exceptions import AccountNotFoundError, ZycusAppError
from src.schemas import AccountHealthBrief, TicketInput, TriageResult
from src.triage import triage_ticket


app = FastAPI(
    title="Zycus AI Support Suite",
    version="1.0.0",
)


class AccountHealthRequest(BaseModel):
    account_id: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResult)
def triage(payload: TicketInput) -> TriageResult:
    try:
        return triage_ticket(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ZycusAppError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/account-health", response_model=AccountHealthBrief)
def account_health(payload: AccountHealthRequest) -> AccountHealthBrief:
    try:
        return summarize_account_health(payload.account_id)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ZycusAppError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/eval")
def evaluation() -> dict:
    from src.evaluation import run_evaluation
    return run_evaluation().model_dump()
