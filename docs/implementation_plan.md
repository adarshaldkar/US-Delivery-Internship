# 🌟 Production-Grade AI Support & TAM Suite — Refined Implementation Plan

> **Assessment:** US Delivery Internship Technical Interview Task Round  
> **Marks:** 100 Core Marks + Up to 10 Bonus Marks (Streamlit +5, Prompt Versioning +2, GitHub CI +2)  
> **Core Philosophy:** Data-First → Hybrid Retrieval → LLM Reasoning → Strict Guardrails & Evidence Verification → Independent Evaluation  

---

## 1. System Architecture

```
                    ZYCUS AI SUPPORT SUITE
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Ticket Triage       Account Health          Evaluation
     (Task 1)             (Task 2)              (Task 3)
        │                     │                     │
        └──────────────┬──────┴─────────────────────┘
                       ▼
              Data / Normalization
          (Dynamic 90-day window anchor)
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     KB Retrieval              Dataset Service
   (Exact + Lexical)           (Tickets & Accounts)
          │                         │
          └────────────┬────────────┘
                       ▼
                  LLM Client
        (OpenAI + Offline Stub Mode)
                       │
                       ▼
              Pydantic Validation
                       │
                       ▼
             Evidence / Guardrails
         (Verbatim Quote Verification)
                       │
                       ▼
                  Final Output
                       │
        ┌──────────────┼─────────────┐
        ▼              ▼             ▼
    Python CLI      FastAPI      Streamlit
  (Single Entry)   (REST API)   (Web UI Demo)
```

---

## 2. Component & Directory Structure

```
zycus-ai-support/
├── data/
│   ├── tickets.json               # 500 support tickets
│   └── accounts.json              # 50 enterprise account summaries
├── knowledge-base/
│   ├── products/                  # 5 product reference docs
│   ├── troubleshooting/           # 2 cross-product troubleshooting guides
│   ├── billing/                   # billing & plans guide
│   └── onboarding/                # onboarding guide
├── src/
│   ├── __init__.py
│   ├── config.py                  # Centralized settings & reference date modes
│   ├── exceptions.py              # Domain error hierarchy (AccountNotFoundError, etc.)
│   ├── schemas.py                 # Strict Pydantic models (Enums, TriageResult, AccountHealthBrief)
│   ├── normalization.py           # Whitespace, PII, timestamp, and field sanitization
│   ├── data_loader.py             # Data loading, joining, and dynamic 90-day ticket filtering
│   ├── retrieval.py               # Markdown section chunker, error-code boost, hybrid lexical retrieval
│   ├── llm_client.py              # OpenAI client + deterministic offline stub for CI
│   ├── validation.py              # Guardrails: quote verification, KB grounding, enum validation
│   ├── triage.py                  # Task 1: Intelligent Ticket Triage Agent
│   ├── account_health.py          # Task 2: TAM Account Health Summariser (Strict 3 Sections)
│   ├── evaluation.py              # Task 3: Independent Evaluation Harness (0.0 to 1.0 scoring)
│   ├── api.py                     # FastAPI REST API (POST /triage, POST /account-health, GET /health)
│   └── main.py                    # Unified CLI single-command runner
├── prompts/
│   ├── registry.json              # Version tracking & changelog
│   ├── triage/
│   │   └── v1.0.0.txt
│   └── account_health/
│       └── v1.0.0.txt
├── eval/
│   ├── test_cases.json            # Curated test cases (standard + adversarial)
│   ├── eval_report.json           # Machine-readable eval output
│   └── eval_report.md             # Markdown summary table
├── .github/
│   └── workflows/
│       └── eval.yml               # Automated CI (runs pytest and offline eval on push)
├── app.py                         # Streamlit Web UI (+5 Bonus)
├── DESIGN.md                      # Production Design Note (~600 words)
├── README.md                      # Comprehensive documentation & Loom link
├── requirements.txt               # Locked dependencies
├── .env.example                   # Clean template (NO API keys committed)
└── .gitignore                     # Git rules blocking .env, caches, logs
```

---

## 3. Phased Implementation Roadmap

### Phase 1: Foundation Layer
1. `src/config.py`: Centralized configuration (`reference_date_mode="dataset_latest"`, paths, models, thresholds).
2. `src/exceptions.py`: Typed domain exceptions (`AccountNotFoundError`, `InvalidTicketError`, `RetrievalError`, `ValidationError`).
3. `src/schemas.py`: Pydantic models for tickets, accounts, triage results, and the 3-section account health brief.
4. `src/normalization.py`: Targeted PII masking, whitespace normalization, null field handling.
5. `src/data_loader.py`: Safe JSON loader, dynamic 90-day windowing relative to dataset max, authoritative `account_id` join with company fallback.
6. `src/retrieval.py`: Section-based chunking on `---`, exact error code boosting (`ERR_CONNECTION_TIMEOUT`, etc.), TF-IDF / BM25 lexical ranking, and confidence scoring.

### Phase 2: LLM Client & Validation Guardrails
1. `src/llm_client.py`: OpenAI integration with structured JSON response formatting + offline deterministic fallback mode.
2. `src/validation.py`: Verbatim quote verification against ticket bodies / escalation notes, KB document existence check, and prompt injection defense.

### Phase 3: Task 1 — Intelligent Ticket Triage Agent
1. Prompt template with untrusted customer data protection (`prompts/triage/v1.0.0.txt`).
2. `src/triage.py`: Ingests raw text/JSON, extracts errors, runs KB retrieval, invokes LLM, validates output, surfaces product, area, category, secondary topics, urgency P1–P4 with reasoning, KB doc + excerpt, recommended team, and draft response.

### Phase 4: Task 2 — TAM Account Health Summariser
1. Prompt template (`prompts/account_health/v1.0.0.txt`).
2. `src/account_health.py`: Retrieves account + dynamic 90-day tickets, detects churn signals, enforces verbatim quotes, generates deterministic **strictly 3-section brief** (Executive Summary, Open Risks & Flagged Issues, Recommended Talking Points).

### Phase 5: Task 3 — Evaluation Harness & Test Suite
1. `eval/test_cases.json`: 10+ test cases (5 Task 1 + 2 adversarial, 5 Task 2 + 2 adversarial) derived from real dataset examples.
2. `src/evaluation.py`: Independent rule-based assertions + weighted scoring ($0.0 \to 1.0$), exports `eval_report.json` and `eval_report.md`.
3. `tests/`: Automated unit and integration tests for `pytest`.

### Phase 6: Task 4 — Production Design Note
1. `DESIGN.md` (~600 words): Failure modes & mitigations, Latency vs Quality, PII masking, 10× Scaling architecture.

### Phase 7: Bonus Features & User Interfaces
1. `app.py`: Streamlit Web UI with 3 tabs (Ticket Triage, Account Health, Live Evaluation Dashboard).
2. `src/api.py`: FastAPI server (`/triage`, `/account-health`, `/health`, `/eval`).
3. `src/main.py`: Single entry-point CLI runner.
4. `.github/workflows/eval.yml`: Automated CI testing offline eval on push.

### Phase 8: Verification & Packaging
1. Verify clean install and run in offline & LLM modes.
2. Complete `README.md`, `.env.example`, `.gitignore`.
