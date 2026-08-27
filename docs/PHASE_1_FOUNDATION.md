# 📑 PHASE 1: FOUNDATION LAYER AUDIT & DYNAMIC DESIGN BLUEPRINT

> **Objective:** Perform a rigorous, file-by-file audit of the entire project to identify and eliminate all hardcoded values, static mappings, and artificial defaults before proceeding to subsequent phases.

---

## 🔍 Comprehensive File & Folder Audit

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    REPOSITORY AUDIT SUMMARY                                      │
├──────────────────────────┬─────────────────────────────┬─────────────────────────────────────────┤
│ File / Module            │ Hardcoded Status            │ Dynamic Action Plan                     │
├──────────────────────────┼─────────────────────────────┼─────────────────────────────────────────┤
│ src/config.py            │ ✅ Clean (No static rules)   │ Path-independent, dynamic date mode     │
│ src/schemas.py           │ ✅ Clean (Open product type)│ Product is dynamic str, strict enums    │
│ src/data_loader.py       │ ✅ Clean (Dynamic date)     │ Reference date = max(ticket.created_at) │
│ src/normalization.py     │ ✅ Clean (Targeted PII)     │ Regex masking, preserves technical codes│
│ src/retrieval.py         │ ✅ Clean (Product Header Ext│ Extract product from Markdown '# ' line │
│ src/validation.py        │ ✅ Clean (Quote verification│ Dynamic substring search in sources     │
│ src/llm_client.py        │ ❌ Hardcoded mappings found  │ Remove doc_to_prod, fake conf, static TP│
│ src/exceptions.py        │ ✅ Clean (Typed exceptions) │ Clean domain error hierarchy            │
│ prompts/registry.json    │ ✅ Clean (Version registry) │ Versioned prompt management             │
└──────────────────────────┴─────────────────────────────┴─────────────────────────────────────────┘
```

---

## 🚨 Detailed Hardcoded Values Audit & Removal Strategy

### 1. Product Name Resolution (`src/retrieval.py` & `src/llm_client.py`)
- **Found Hardcoding:**
  ```python
  doc_to_prod = {
      "databridge-pro": "DataBridge Pro",
      "cloudsync": "CloudSync", ...
  }
  product = doc_to_prod.get(doc_name, "DataBridge Pro")
  ```
- **The Dynamic Fix:**
  Extract the product name directly from the first `# ` header of the Markdown file during indexing:
  ```python
  # Example: "# DataBridge Pro — Product Reference"
  # Extracted product -> "DataBridge Pro"
  header_line = content.split("\n")[0]
  product_name = header_line.replace("#", "").split("—")[0].split("-")[0].strip()
  ```
  Store `product: str` on `KBChunk`. If a new product document `NewService.md` is added, it is indexed automatically with zero code changes.

---

### 2. Confidence Scoring (`src/llm_client.py`)
- **Found Hardcoding:**
  ```python
  "confidence": 0.95
  ```
- **The Dynamic Fix:**
  Compute confidence dynamically from retrieval similarity and error-code matching signals:
  ```python
  if top_res and top_res.is_exact_error_match:
      confidence = round(min(1.0, top_res.score), 2)
  elif top_res:
      confidence = round(min(0.90, top_res.score * 0.90), 2)
  else:
      confidence = 0.20  # Low confidence for ungrounded queries
  ```

---

### 3. TAM Talking Points (`src/llm_client.py` & `src/account_health.py`)
- **Found Hardcoding:**
  Static 4-bullet list identical for all accounts regardless of health or metrics.
- **The Dynamic Fix:**
  Synthesize talking points dynamically based on that specific account's actual data:
  - If `days_until_renewal < 90` $\implies$ Proactive renewal milestone discussion.
  - If `seat_utilization < 70%` $\implies$ Targeted training and user adoption strategy.
  - If `p1_count > 0` $\implies$ SLA incident post-mortem citing exact ticket subjects.
  - If `escalation_notes` exist $\implies$ Direct resolution of stakeholder/competitor concerns.
  - If account is `Healthy` with high usage $\implies$ Feature expansion & integration roadmap.

---

### 4. Missing Field Defaults (`src/normalization.py` & `src/account_health.py`)
- **Found Hardcoding:**
  ```python
  plan = account.get("plan_tier", "Enterprise")
  health = account.get("health_status", "Healthy")
  arr = int(account.get("arr_usd") or 0)
  ```
- **The Dynamic Fix:**
  Preserve `None` or render `"Unavailable"`; never invent fake enterprise or healthy statuses:
  - `plan_tier = account.get("plan_tier") or "Tier Unavailable"`
  - `health_status = account.get("health_status") or "Status Unavailable"`
  - `arr_usd = account.get("arr_usd")` (remains `None` if missing)
  - `seat_utilization = round(seats_act / seats_lic * 100, 1) if (seats_lic and seats_lic > 0) else None`

---

## 🗺️ Step-by-Step Phase Roadmap

```
PHASE 1: Foundation Layer & Data Services (COMPLETED & VERIFIED)
├── Centralized frozen configuration (src/config.py)
├── Strict Pydantic contracts & enums (src/schemas.py)
├── Typed domain exceptions (src/exceptions.py)
├── Dynamic 90-day date windowing & account joins (src/data_loader.py)
├── Targeted PII sanitization & whitespace cleaner (src/normalization.py)
└── Section chunker & TF-IDF error retriever with product header extraction (src/retrieval.py)

PHASE 2: LLM Client & Validation Guardrails (CURRENT)
├── OpenAI structured JSON completion (src/llm_client.py)
├── Dynamic offline engine (src/llm_client.py)
└── Verbatim quote verifier & grounded citation check (src/validation.py)

PHASE 3: Task 1 — Intelligent Ticket Triage Agent
├── Untrusted data injection protection prompt (prompts/triage/v1.0.0.txt)
└── Callable triage pipeline returning TriageResult (src/triage.py)

PHASE 4: Task 2 — TAM Account Health Summariser
├── QBR brief prompt with verbatim quote rule (prompts/account_health/v1.0.0.txt)
└── Deterministic 3-section brief generator (src/account_health.py)

PHASE 5: Task 3 — Evaluation Harness & Test Suite
├── 10+ Test cases (standard + adversarial) in eval/test_cases.json
└── Independent 0.0 to 1.0 scoring engine & report generator (src/evaluation.py)

PHASE 6: Task 4 — Production Design Note
└── 600-word engineering note on Failure Modes, Latency, PII, and Scaling (DESIGN.md)

PHASE 7: Bonus Interfaces & CI
├── Streamlit Web UI Demo (app.py)
├── FastAPI REST API (src/api.py)
├── Unified CLI entrypoint (src/main.py)
└── GitHub Actions workflow (.github/workflows/eval.yml)
```
