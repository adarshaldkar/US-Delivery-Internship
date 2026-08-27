# 🌟 PRODUCTION-GRADE AI SUITE: ADVANCED MASTER BLUEPRINT & SCRIPT
## US Delivery Internship — Technical Interview Task Round

---

## 📑 TABLE OF CONTENTS
1. [Official Assessment Context & Deliverables](#1-official-assessment-context--deliverables)
2. [Dataset Anatomy & Dynamic Date Anchoring](#2-dataset-anatomy--dynamic-date-anchoring)
3. [The 35 Production Edge Cases & Defensive Guardrails Matrix](#3-the-35-production-edge-cases--defensive-guardrails-matrix)
4. [System Architecture & The "Zero-Hardcoding" Principle](#4-system-architecture--the-zero-hardcoding-principle)
5. [The Validation & Guardrail Verification Layer](#5-the-validation--guardrail-verification-layer)
6. [Task 1: Intelligent Ticket Triage Agent (Deep Spec)](#6-task-1-intelligent-ticket-triage-agent-deep-spec)
7. [Task 2: TAM Account Health Summariser (Deep Spec)](#7-task-2-tam-account-health-summariser-deep-spec)
8. [Task 3: Independent Evaluation Harness & Weighted Scoring](#8-task-3-independent-evaluation-harness--weighted-scoring)
9. [Task 4: Production Design Note Specification (~600 Words)](#9-task-4-production-design-note-specification-600-words)
10. [Bonus Features & UI Specification](#10-bonus-features--ui-specification)
11. [Submission Rules & Automatic Disqualifier Checklist](#11-submission-rules--automatic-disqualifier-checklist)
12. [Loom Video Walkthrough Script (Target: 4.5 Minutes)](#12-loom-video-walkthrough-script-target-45-minutes)
13. [Step-by-Step Implementation Sequence](#13-step-by-step-implementation-sequence)

---

# 1. OFFICIAL ASSESSMENT CONTEXT & DELIVERABLES

- **Role / Theme:** US Delivery Internship — Production-grade AI for Technical Support & Technical Account Management (TAM) Teams.
- **Marks Distribution:**
  - **Task 1: Intelligent Ticket Triage Agent** — 30 Marks
  - **Task 2: TAM Account Health Summariser** — 25 Marks
  - **Task 3: Evaluation Harness** — 20 Marks
  - **Task 4: Production Design Note** — 15 Marks
  - **Bonus Points** — Up to +10 Marks (Streamlit UI +5, Streaming +3, CI +2, Prompt Versioning +2)
  - **Total Marks Available:** 110 / 100
- **Official Deadline:** 48 hours from repository link sharing (*Internal execution target: within current session*).
- **Core Deliverables:**
  1. Public/Shared GitHub Repository.
  2. Top-level `README.md` with setup instructions, sample runs, and design note link.
  3. `requirements.txt` running cleanly from a fresh environment.
  4. `.env.example` showing required environment variables (never committed real keys).
  5. Evaluation report (`eval/eval_report.json` and `eval/eval_report.md`).
  6. **Loom Walkthrough Video (3 to 6 minutes strictly)** demonstrating code, live Tasks 1 & 2, and eval results.

---

# 2. DATASET ANATOMY & DYNAMIC DATE ANCHORING

### 🚨 Critical Discovery: Dynamic Date Anchoring vs. Hardcoded Timestamps
- **The Data Range:** The 500 tickets in `tickets.json` range from **2026-02-20** to **2026-05-22** (~91 days).
- **The Pitfall:** Naïvely calculating `datetime.now() - timedelta(days=90)` in August 2026 filters out 100% of tickets, causing an empty history bug across all accounts.
- **The Production-Grade Solution:** Dynamically anchor the 90-day window to the latest ticket timestamp present in the active dataset:
  ```python
  from datetime import datetime, timedelta, timezone

  def get_90d_ticket_window(tickets: list, account_id: str, company: str = None) -> list:
      if not tickets:
          return []
      
      # 1. Parse timestamps dynamically
      parsed_dates = [
          datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
          for t in tickets if "created_at" in t
      ]
      if not parsed_dates:
          return []
      
      # 2. Calculate dynamic reference anchor
      reference_date = max(parsed_dates)
      cutoff_date = reference_date - timedelta(days=90)
      
      # 3. Filter tickets within the dynamic 90-day window
      return [
          t for t in tickets
          if (t.get("account_id") == account_id or (company and t.get("company") == company))
          and datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) >= cutoff_date
      ]
  ```

### Dataset Distribution Overview:
- **500 Support Tickets (`data/tickets.json`):**
  - Products: `DataBridge Pro` (89), `AnalyticsHub` (101), `CloudSync` (84), `SecureVault` (123), `WorkflowEngine` (103).
  - Categories: `Billing` (50), `Integration` (50), `How-To` (66), `Data Loss` (73), `Bug` (59), `Feature Request` (71), `Onboarding` (63), `Performance` (68).
  - Urgencies: `P1` (14), `P2` (110), `P3` (217), `P4` (159).
  - Statuses: `Open`, `In Progress`, `Pending Customer`, `Resolved`, `Closed`.
- **50 Account Summaries (`data/accounts.json`):**
  - Health: `Healthy`, `At Risk`, `Churning`, `New`.
  - Usage Trend: `Increasing`, `Stable`, `Declining`, `Inactive`.
  - Qualitative notes: `escalation_notes` containing unstructured churn indicators.
- **9 Knowledge Base Markdown Documents (`knowledge-base/`):**
  - Products: `databridge-pro.md`, `cloudsync.md`, `analyticshub.md`, `securevault.md`, `workflowengine.md`.
  - Troubleshooting: `authentication-sso.md`, `performance-and-integrations.md`.
  - Billing & Onboarding: `billing-and-plans.md`, `onboarding-guide.md`.

---

# 3. THE 35 PRODUCTION EDGE CASES & DEFENSIVE GUARDRAILS MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DEFENSIVE GUARDRAIL TAXONOMY                                    │
├──────────────────────────────┬───────────────────────────────┬──────────────────────────────────┤
│ 1. Invalid Account ID        │ 13. Unknown KB Issue          │ 25. Malformed KB Document        │
│ 2. Account with 0 Tickets    │ 14. Multiple KB Doc Matches   │ 26. KB Retrieval Zero Results    │
│ 3. Missing / Null NPS Score  │ 15. Exact Error Code Boost    │ 27. Offline / Missing API Key    │
│ 4. Missing Escalation Notes  │ 16. Hallucinated KB Citation  │ 28. Malformed LLM JSON Response  │
│ 5. Account ID Mismatch       │ 17. Hallucinated Churn Quote  │ 29. Invalid Enum Classification  │
│ 6. Account vs Co. Mismatch   │ 18. Wrong Evidence Source     │ 30. Non-Deterministic Output     │
│ 7. Empty Ticket Input        │ 19. False Churn Signal        │ 31. Circular Eval Logic          │
│ 8. Subject Only Input        │ 20. Resolved vs Open Status   │ 32. Dynamic Production vs Static │
│ 9. Body Only Input           │ 21. P1 Spike Inconsistency    │ 33. Real-Data Ground Truth Tests │
│ 10. Massive Ticket String    │ 22. Dynamic Seat Utilization  │ 34. Component-Weighted Quality   │
│ 11. Multi-Topic Ticket       │ 23. Days to Renewal Proximity │ 35. True Adversarial Test Cases  │
│ 12. Ticket Without Error Code│ 24. Missing Account Fields    │                                  │
└──────────────────────────────┴───────────────────────────────┴──────────────────────────────────┘
```

### Detailed Edge Case Handling Specifications:

1. **Invalid Account ID (`ACC-9999`):** Returns structured JSON `{ "error": "ACCOUNT_NOT_FOUND", "account_id": "ACC-9999" }` with 404 status, zero unhandled Python exceptions.
2. **Account Exists with Zero 90-day Tickets:** Executive summary explicitly notes zero tickets in the active window; risk analysis is synthesized cleanly from `escalation_notes`, `usage_trend`, and seat metrics without index crashes.
3. **Missing NPS Score (`"nps_score": null`):** Normalized to `"NPS unavailable (no survey submitted)"`; never defaults to 0 or hallucinated numbers.
4. **Missing Escalation Notes:** States `"Escalation signals: None identified from account notes."` (Preserving the principle: *Absence of evidence ≠ evidence of absence*).
5. **Account ID Discrepancy:** Authoritative lookup by exact `account_id` first; fallback to exact normalized `company` match second; unmatched returns structured error.
6. **Conflicting Account ID vs Company:** When `account_id` exists but company name differs, trusts authoritative `account_id` and adds `"data_quality_warning": "ACCOUNT_COMPANY_MISMATCH"`.
7. **Empty Ticket Text (`subject=""`, `body=""`):** Caught in pre-validation layer before LLM invocation, returning `"INVALID_TICKET: Ticket subject and body cannot both be empty."`
8. **Subject-Only Ticket:** Valid; classifies based on subject semantic payload.
9. **Body-Only Ticket:** Valid; extracts implied context and classifies cleanly.
10. **Extremely Long Ticket (>4000 chars):** Guardrail applies safe chunk truncation / token budgeting without altering core error tokens or hardcoding urgency based on length.
11. **Multi-Topic Ticket (e.g. Billing + Timeout + SSO):** Identifies dominant primary `category` by severity, and returns `secondary_topics: ["Billing", "Integration"]` with holistic reasoning.
12. **No Error Code Present ("dashboard spins forever"):** Fallback from exact regex matching to lexical BM25 + TF-IDF semantic cosine similarity.
13. **Unknown / Out-of-Scope Issue:** If KB retrieval confidence is below threshold, returns `is_known_issue: false`, `matched_kb_document: null`, rather than hallucinating a match.
14. **Multiple Matching KB Documents:** Retrieves top-$k$ candidate chunks, scores relevance, and selects the highest-scoring section as primary evidence while supplying secondary context.
15. **Exact Error Code Matching:** Exact error token hits (e.g. `ERR_CONNECTION_TIMEOUT`) receive explicit relevance multiplier over purely semantic similarity.
16. **Hallucinated KB Citations:** Guardrail verifies that `matched_kb_document` belongs to the retrieved candidate set; rejects or repairs invalid citations.
17. **Hallucinated Churn Quotes:** Guardrail performs normalized substring search against the raw ticket bodies and `escalation_notes`. If quote is not found verbatim, the flag is rejected.
18. **Quote Source Traceability:** Each flagged risk strictly attributes source: `{ "source": "ticket", "ticket_id": "TKT-10042", "quote": "..." }` or `{ "source": "escalation_note", "quote": "..." }`.
19. **No Churn Signals Present:** Correctly outputs `"No explicit churn or escalation signals identified"` rather than inventing false alarms.
20. **Resolved vs Open Ticket Status:** Distinguishes active risks (Open/In Progress) from historical resolution records (Resolved/Closed).
21. **P1 Spike Discrepancy Detection:** Reconciles `account["p1_tickets_last_30d"]` with filtered ticket count; flags `P1_COUNT_MISMATCH` if metadata differs from actual records.
22. **Dynamic Seat Utilization:** Dynamically calculates `utilization_rate = round(seats_active / seats_licensed * 100, 1)` without hardcoded thresholds.
23. **Renewal Date Proximity:** Calculates dynamic `days_until_renewal` from reference date and surfaces proximity as contextual reasoning for the TAM.
24. **Missing / Malformed Account Fields:** Pydantic models with default fallbacks (`get("products", [])`, `get("integrations_active", [])`).
25. **Malformed KB Document:** Chunker skips individual corrupted files with a warning, preserving full engine operation.
26. **KB Retrieval with 0 Results:** Cleanly returns `{ "matches": [], "confidence": 0.0 }`.
27. **Offline / Missing API Keys:** Automatically triggers local deterministic rule & embedding fallback engine, ensuring 100% CI pass rate.
28. **Malformed LLM JSON Response:** Structured repair layer with Pydantic JSON parser and retry mechanism.
29. **Invalid Enum Output:** Enforces strict Pydantic enum validation (`P1`-`P4`, 8 standard categories).
30. **Deterministic Output:** Fixed `temperature=0.0`, fixed random seed, deterministic prompt formatting, and stable alphabetical key sorting.
31. **Independent Evaluation Logic:** Eval harness uses separate assertion logic and validation rules rather than reusing production inference code.
32. **Static Evaluation vs. Dynamic Production:** Production pipeline is completely dynamic; test suite utilizes curated static test fixtures from real data.
33. **Real-Data Ground Truth:** Test fixtures represent verified ground-truth tickets across all 4 urgency tiers, multi-topic tickets, and missing account edge cases.
34. **Component-Weighted Quality Score:** Quality score calculated across 6 objective sub-dimensions ($0.0 \to 1.0$).
35. **Genuine Adversarial Test Cases:** Includes empty payloads, corrupted IDs, conflicting company names, and multi-issue edge cases.

---

# 4. SYSTEM ARCHITECTURE & THE "ZERO-HARDCODING" PRINCIPLE

### The Principle:
The system dynamically loads its taxonomy, categories, products, and error codes **directly from data and markdown files**. No brittle hardcoded dictionaries (e.g. `if category == "Billing": return "Billing Support"`).

```
                              DATA-CENTRIC ARCHITECTURE
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
            tickets.json            accounts.json          knowledge-base/
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          ▼
                                 Data Loader & Chunker
                                          │
                                          ▼
                             Hybrid KB Retrieval Engine
                       (Exact Regex + BM25 + TF-IDF Cosine)
                                          │
                                          ▼
                                Prompt & LLM Engine
                                          │
                                          ▼
                              Guardrail / Validation
                         (Quote Check + Enum Verification)
                                          │
                                          ▼
                              Validated Output Schema
```

### Proposed Directory Layout:
```
zycus-ai-support/
├── data/
│   ├── tickets.json               # 500 support tickets
│   └── accounts.json              # 50 enterprise account summaries
├── knowledge-base/
│   ├── products/                  # 5 product reference docs
│   ├── troubleshooting/           # 2 cross-product troubleshooting guides
│   ├── billing/                   # billing and plan guides
│   └── onboarding/                # onboarding guide
├── src/
│   ├── __init__.py
│   ├── config.py                  # Environment config & dynamic paths
│   ├── data_loader.py             # Data loading, joining, and dynamic date windowing
│   ├── schemas.py                 # Pydantic data models & enums
│   ├── retrieval.py               # Section-based KB chunker & hybrid retriever
│   ├── llm_client.py              # LLM client with local deterministic fallback
│   ├── validation.py              # Quote validation, KB citation check, enum verification
│   ├── triage.py                  # Task 1 Intelligent Ticket Triage Agent
│   ├── account_health.py          # Task 2 TAM Account Health Summariser
│   ├── evaluation.py              # Task 3 Evaluation Harness & Report Generator
│   ├── api.py                     # FastAPI REST API endpoints
│   └── main.py                    # Unified CLI entrypoint
├── prompts/
│   ├── registry.json              # Version tracking & changelog
│   ├── triage_v1.txt              # Task 1 prompt template
│   └── account_health_v1.txt      # Task 2 prompt template
├── eval/
│   ├── test_cases.json            # Curated test suite (including adversarial cases)
│   ├── eval_report.json           # Machine-readable evaluation report
│   └── eval_report.md             # Formatted markdown summary report
├── .github/
│   └── workflows/
│       └── eval.yml               # Automated GitHub Actions CI workflow
├── app.py                         # Streamlit Web UI Demo (+5 Bonus)
├── DESIGN.md                      # Production Design Note (~600 words)
├── README.md                      # Comprehensive project documentation
├── requirements.txt               # Locked dependencies
├── .env.example                   # Environment variable template
└── .gitignore                     # Git ignore rules (blocking .env & caches)
```

---

# 5. THE VALIDATION & GUARDRAIL VERIFICATION LAYER

To guarantee production reliability, every inference pass goes through strict post-processing:

```
                  ┌────────────────────────────────────────┐
                  │          Raw LLM Response JSON         │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 1. Pydantic Schema & Enum Validation   │
                  │    • Validate Urgency in [P1..P4]      │
                  │    • Validate Category in 8 enums      │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 2. Verbatim Quote Verification         │
                  │    • normalized_quote in ticket_body?  │
                  │    • normalized_quote in escalations?  │
                  │    • If NOT found -> Reject flag       │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ 3. KB Grounding & Document Check       │
                  │    • Is cited doc in retrieved set?    │
                  │    • If NOT -> Set doc=None, known=F   │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       Validated, Traceable Output      │
                  └────────────────────────────────────────┘
```

---

# 6. TASK 1: INTELLIGENT TICKET TRIAGE AGENT (DEEP SPEC)

- **Marks:** 30 Marks
- **Input:** Raw ticket string OR JSON dictionary with `subject` and `body`.
- **Classification Dimensions:**
  1. `product`: Name of product.
  2. `product_area`: Module/feature area.
  3. `category`: One of 8 standard categories (`Bug`, `Feature Request`, `How-To`, `Performance`, `Billing`, `Integration`, `Onboarding`, `Data Loss`).
  4. `secondary_topics`: List of additional mentioned topic areas (for multi-topic handling).
  5. `urgency`: `P1`, `P2`, `P3`, `P4`.
  6. `urgency_reasoning`: Clear technical justification.
  7. `is_known_issue`: Boolean flag.
  8. `matched_kb_document`: Path of relevant KB doc.
  9. `kb_resolution_steps`: Troubleshooting steps from KB.
  10. `recommended_team`: Appropriate responder team based on issue domain.
  11. `draft_response`: Empathetic, actionable draft response.
- **Python Interface:**
  ```python
  from src.triage import triage_ticket
  result = triage_ticket({"subject": "Timeout in connector", "body": "ERR_CONNECTION_TIMEOUT after 30s"})
  ```
- **REST Endpoint:** `POST /triage`

---

# 7. TASK 2: TAM ACCOUNT HEALTH SUMMARISER (DEEP SPEC)

- **Marks:** 25 Marks
- **Input:** `account_id: str` (e.g. `"ACC-3336"`, `"ACC-4654"`).
- **Core Operations:**
  1. Lookup account in `accounts.json` with fallback company resolution.
  2. Retrieve last 90 days of tickets using the dynamic reference window.
  3. Compute metrics: active seat utilization %, 90d ticket volume, P1 spike count, renewal proximity.
  4. Extract churn and escalation signals, enforcing **direct verbatim quotes**.
  5. Generate deterministic 3-part brief.
- **Output Structure:**
  - **Section 1: Executive Summary (3–5 sentences):** Business health, seat adoption, ticket velocity, contract timeline.
  - **Section 2: Open Risks & Flagged Issues:** Each risk accompanied by severity, signal source, and exact verbatim quote.
  - **Section 3: Recommended Talking Points for TAM:** Strategic QBR discussion points, remediation steps, and expansion opportunities.
- **Python Interface:**
  ```python
  from src.account_health import summarize_account_health
  brief = summarize_account_health("ACC-3336")
  ```
- **REST Endpoint:** `POST /account-health/{account_id}`

---

# 8. TASK 3: INDEPENDENT EVALUATION HARNESS & WEIGHTED SCORING

- **Marks:** 20 Marks
- **Test Suite Structure (`eval/test_cases.json`):**
  - **Task 1 Cases (5 Standard + 2 Adversarial):**
    - Standard: Critical Bug (P1), Performance Timeout (P2), How-To Query (P3), Cosmetic/Minor (P4), Billing Dispute.
    - Adversarial: Empty ticket payload, multi-topic overlapping ticket (Billing + Data Loss).
  - **Task 2 Cases (5 Standard + 2 Adversarial):**
    - Standard: High-risk churning enterprise account, Healthy stable account, Declining usage account, Low NPS account.
    - Adversarial: Non-existent account ID (`ACC-9999`), Account with 0 tickets in 90 days.
- **Scoring Function & Weighted Quality Rubric ($0.0 \to 1.0$):**
  $$\text{Quality Score} = 0.25 \times S_{\text{Product}} + 0.25 \times S_{\text{Category}} + 0.20 \times S_{\text{Urgency}} + 0.15 \times S_{\text{KB}} + 0.10 \times S_{\text{Schema}} + 0.05 \times S_{\text{Reasoning}}$$
- **Outputs:**
  - `eval/eval_report.json`
  - `eval/eval_report.md` (Formatted markdown table with latency, quality score, and pass/fail status).

---

# 9. TASK 4: PRODUCTION DESIGN NOTE SPECIFICATION (~600 WORDS)

- **Marks:** 15 Marks
- **Location:** `DESIGN.md` and linked in `README.md`.
- **Mandatory Sections to Address:**
  1. **Top 3 Production Failure Modes & Mitigations:**
     - *Failure 1: Triage Misclassification / P1 Escalation Storm.* Mitigation: Confidence scoring threshold; human-in-the-loop review for edge scores; fallback to Tier-1 queue.
     - *Failure 2: Knowledge Base Drift & Stale Error Codes.* Mitigation: Automated KB document indexing CI check; telemetry on zero-match error codes; version tagging.
     - *Failure 3: External LLM Outage / Rate Limit Throttling.* Mitigation: Local deterministic fallback engine; exponential backoff retries; circuit breakers.
  2. **Latency vs. Quality Trade-offs:**
     - *Design Choice:* Sub-10ms local TF-IDF/BM25 retrieval paired with single-pass structured LLM inference rather than multi-agent debate loops.
     - *If Latency Were Hard Constraint (<200ms):* Speculative classification via small distilled local model (e.g. SetFit / ONNX) with asynchronous KB enrichment.
  3. **Data Sensitivity & PII Handling:**
     - Pre-LLM PII sanitization pipeline (regex masking for emails, phone numbers, IP addresses, credit cards, and API tokens) ensuring zero customer PII reaches external API logs.
  4. **Scaling to 10× Ticket Volume:**
     - *Bottlenecks:* Synchronous LLM calls, repetitive sequential file I/O.
     - *Scaling Architecture:* Asynchronous message queue (Celery/RabbitMQ), persistent Redis/ChromaDB vector caching, horizontally scalable worker pools.

---

# 10. BONUS FEATURES & UI SPECIFICATION

1. **Streamlit Interactive UI (+5 Marks):**
   - Clean, professional dark/light UI (`app.py`) with 3 tabs:
     - **Tab 1: Ticket Triage Agent** (Live input text box, instant classification badges, KB document viewer, draft response generator).
     - **Tab 2: TAM Account Health Brief** (Account ID selector, real-time metric cards, risk highlights with quote callouts, QBR talking points).
     - **Tab 3: Evaluation & Telemetry Dashboard** (Live test runner, quality score meters, adversarial edge case visualizer).
2. **Streaming Response Support (+3 Marks):**
   - Streaming generator for draft response and executive summary generation.
3. **Automated GitHub Actions CI (+2 Marks):**
   - `.github/workflows/eval.yml` runs test suite and eval harness on every push.
4. **Prompt Version Registry (+2 Marks):**
   - `prompts/registry.json` tracking prompt version IDs, authors, and changelog.

---

# 11. SUBMISSION RULES & AUTOMATIC DISQUALIFIER CHECKLIST

| ❌ Automatic Disqualifier | ✅ Our Built-in Prevention Mechanism |
| :--- | :--- |
| **API key committed in any form** | `.gitignore` explicitly excludes `.env`, `*.key`, `*.token`. Clean `.env.example` provided. |
| **Fails on clean `pip install -r requirements.txt`** | Strict version locking in `requirements.txt` with zero conflicting dependencies. |
| **Fails single entry-point run command** | `python src/main.py --eval` or `python src/main.py --all` executes end-to-end cleanly. |
| **Using external / scraped data** | Strictly uses the provided 500 tickets, 50 accounts, and 9 KB docs. |
| **Loom video absent or under 3 minutes** | Structured script targets **4.5 minutes** (safe middle of the 3–6 min official window). |

---

# 12. LOOM VIDEO WALKTHROUGH SCRIPT (TARGET: 4.5 MINUTES)

### ⏱️ Minute-by-Minute Guide:

- **0:00 – 0:45 | Architecture & Context:**
  - *"Hi! This is the walkthrough for the US Delivery Internship AI Support & TAM Platform."*
  - Show VS Code structure: `src/` (core logic, retrieval, validation), `data/` (500 tickets, 50 accounts), `knowledge-base/` (9 docs), `eval/` (test cases and reports).
  - Highlight key architectural decisions: **Zero-hardcoded taxonomy**, **Dynamic 90-day date anchoring**, and **Verbatim quote verification**.

- **0:45 – 1:45 | Task 1 Demo: Intelligent Ticket Triage:**
  - Launch Streamlit UI (`streamlit run app.py`).
  - Enter ticket with error code: *"Our DataBridge Pro pipeline failed with ERR_CONNECTION_TIMEOUT after 30s."*
  - Show live result: Product (`DataBridge Pro`), Category (`Bug/Performance`), Urgency (`P2` with impact reasoning), Matched KB (`databridge-pro.md`), Routing Team (`Tier-2 Data Platform`), and Draft First Response.
  - Enter an adversarial ticket (e.g. multi-topic or unknown issue) to demonstrate graceful degradation and `secondary_topics`.

- **1:45 – 2:45 | Task 2 Demo: TAM Account Health Brief:**
  - Switch to Account Health tab, enter account ID `ACC-3336`.
  - Point out the 3 sections:
    1. **Executive Summary:** Synthesizes usage trend, ARR, and 90-day ticket volume.
    2. **Open Risks & Churn Signals:** Highlight the exact **verbatim quotes** extracted from ticket bodies and escalation notes.
    3. **TAM Talking Points:** Strategic talking points for the upcoming QBR.
  - Demonstrate deterministic output by re-running and showing identical results.

- **2:45 – 3:45 | Task 3 Demo: Evaluation Harness & Adversarial Tests:**
  - Switch to terminal and run: `python src/main.py --eval`.
  - Show the output table: 10+ test cases, quality scores ($0.0 \to 1.0$), pass/fail results.
  - Explain how adversarial cases (empty ticket, missing account `ACC-9999`, account with 0 tickets) pass cleanly with high quality scores.
  - Show generated `eval_report.md` and `eval_report.json`.

- **3:45 – 4:30 | Task 4 Design Note & Conclusion:**
  - Briefly highlight `DESIGN.md`: Failure modes, Latency trade-offs, PII masking, and 10× Scaling architecture.
  - Mention bonus features: Streamlit UI (+5), GitHub Actions CI (+2), Prompt Registry (+2).
  - *"Thank you for your review!"*

---

# 13. STEP-BY-STEP IMPLEMENTATION SEQUENCE

```text
Step 1: src/config.py & src/data_loader.py (Dynamic date windowing & account joins)
   ↓
Step 2: src/retrieval.py (Section-based chunking & hybrid BM25 + TF-IDF error search)
   ↓
Step 3: src/schemas.py & src/validation.py (Pydantic models & quote/citation guardrails)
   ↓
Step 4: src/llm_client.py (Multi-provider LLM + local deterministic fallback)
   ↓
Step 5: src/triage.py & prompts/ (Task 1 classification & response generation)
   ↓
Step 6: src/account_health.py (Task 2 TAM brief & verbatim quote extraction)
   ↓
Step 7: src/evaluation.py & eval/test_cases.json (Task 3 evaluation harness & reports)
   ↓
Step 8: src/api.py & src/main.py (FastAPI endpoints & unified CLI entrypoint)
   ↓
Step 9: app.py (Streamlit Web UI demo)
   ↓
Step 10: DESIGN.md, README.md, requirements.txt, .env.example, .gitignore, .github/workflows/eval.yml
```
