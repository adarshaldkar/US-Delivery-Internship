"""Centralized immutable configuration for the Zycus AI Support Suite."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class PathsSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    tickets_path: Path = BASE_DIR / "data" / "tickets.json"
    accounts_path: Path = BASE_DIR / "data" / "accounts.json"
    kb_dir: Path = BASE_DIR / "knowledge-base"
    prompts_dir: Path = BASE_DIR / "prompts"
    eval_dir: Path = BASE_DIR / "eval"
    logs_dir: Path = BASE_DIR / "logs"


class LLMSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    seed: int = Field(default=42, ge=0)
    execution_mode: Literal["auto", "llm", "offline"] = Field(
        default_factory=lambda: os.getenv("EXECUTION_MODE", "auto")
    )
    request_timeout_seconds: float = Field(default=45.0, gt=0.0)


class RetrievalSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    top_k: int = Field(default=4, ge=1, le=20)
    exact_error_boost: float = Field(default=0.35, ge=0.0, le=1.0)
    min_confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0)
    historical_ticket_neighbors: int = Field(default=5, ge=1, le=20)


class DataSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference_date_mode: Literal["dataset_latest", "current_time"] = "dataset_latest"
    ticket_history_days: int = Field(default=90, ge=1)


class GuardrailSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_ticket_length: int = Field(default=4000, ge=100)
    strict_quote_verification: bool = True
    strict_kb_grounding: bool = True
    enable_pii_masking: bool = True


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    paths: PathsSettings = Field(default_factory=PathsSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    guardrails: GuardrailSettings = Field(default_factory=GuardrailSettings)


settings = Settings()


def validate_paths(cfg: Settings = settings) -> None:
    """Validate required inputs and create output directories."""
    missing: list[str] = []

    if not cfg.paths.tickets_path.is_file():
        missing.append(f"Tickets dataset missing: {cfg.paths.tickets_path}")
    if not cfg.paths.accounts_path.is_file():
        missing.append(f"Accounts dataset missing: {cfg.paths.accounts_path}")
    if not cfg.paths.kb_dir.is_dir():
        missing.append(f"Knowledge base directory missing: {cfg.paths.kb_dir}")

    if missing:
        raise FileNotFoundError(
            "Configuration path validation failed:\n"
            + "\n".join(f" - {item}" for item in missing)
        )

    cfg.paths.logs_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.eval_dir.mkdir(parents=True, exist_ok=True)
