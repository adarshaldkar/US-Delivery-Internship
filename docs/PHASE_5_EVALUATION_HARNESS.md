# 📑 PHASE 5: TASK 3 — EVALUATION HARNESS & TEST SUITE BLUEPRINT

> **Objective:** Design and implement an independent, reproducible evaluation engine that executes 10+ standard and adversarial test cases across Task 1 and Task 2, calculates weighted 0.0–1.0 quality scores, and automatically generates structured evaluation reports in both JSON and Markdown formats.

---

## 🏗️ 1. Architecture of the Evaluation Harness

```
                           eval/test_cases.json
                         (10+ Diverse Test Cases)
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   Evaluation Runner   │
                        │  (src/evaluation.py)  │
                        └───────────┬───────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────┐                         ┌───────────────────────┐
│   Task 1 Evaluator    │                         │   Task 2 Evaluator    │
│  (triage_ticket)      │                         │ (summarize_account)   │
├───────────────────────┤                         ├───────────────────────┤
│ • Schema Compliance   │                         │ • Schema Compliance   │
│ • Category Accuracy   │                         │ • Executive Summary   │
│ • Urgency Accuracy    │                         │ • Verbatim Quotes     │
│ • KB Citation Check   │                         │ • Talking Points      │
│ • Injection Defense   │                         │ • Metric Fidelity     │
└──────────┬────────────┘                         └──────────┬────────────┘
           │                                                 │
           └────────────────────────┬────────────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │  Weighted Quality     │
                        │  Scoring (0.0 to 1.0) │
                        └───────────┬───────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌───────────────────────┐                         ┌───────────────────────┐
│  eval/eval_report.json│                         │  eval/eval_report.md  │
│  (Machine-Readable)   │                         │  (Human-Readable MD)  │
└───────────────────────┘                         └───────────────────────┘
```

---

## 📋 2. Test Case Suite Specification (`eval/test_cases.json`)

The test suite will contain **12 diverse test cases** representing real-world production support challenges:

| Test ID | Task | Scenario / Test Name | Key Expectations / Validation Criteria | Adversarial? |
| :--- | :--- | :--- | :--- | :---: |
| `TC-01` | Task 1 | Known Error (`ERR_CONNECTION_TIMEOUT`) | `is_known_issue=True`, `matched_kb_document` cited, `urgency` in P1/P2 | No |
| `TC-02` | Task 1 | SAML SSO Integration Query | `category="Integration"`, `product="SecureVault"`, `urgency` in P2/P3 | No |
| `TC-03` | Task 1 | Billing & Invoice Overcharge | `category="Billing"`, `urgency="P3"`, recommended team relates to Billing | No |
| `TC-04` | Task 1 | Multi-Topic (Billing + SAML Auth) | Primary category identified + `secondary_topics` captures second theme | No |
| `TC-05` | Task 1 | Data Loss & Corruption Outage | `category="Data Loss"`, `urgency="P1"`, non-empty draft response | No |
| `TC-06` | Task 1 | Feature Request (CSV Export) | `category="Feature Request"`, `urgency="P4"` | No |
| `TC-07` | Task 1 | Ambiguous / Minimal Input (Subject Only) | Valid `TriageResult` returned without crashing, `confidence < 0.85` | No |
| `TC-08` | Task 1 | **Prompt Injection Attack** | Does not reveal system prompt, remains focused on triage classification | **Yes** |
| `TC-09` | Task 2 | High-ARR At-Risk Account (`ACC-3336`) | 3-section brief, verbatim quotes from escalation notes, renewal talking point | No |
| `TC-10` | Task 2 | Zero-Ticket Account (`ACC-1002`) | Gracefully reports 0 tickets in 90 days, no fabricated risks | No |
| `TC-11` | Task 2 | Churning Account with Declining Usage | Highlights declining usage and low seat utilization in talking points | No |
| `TC-12` | Task 2 | **Unknown Account ID (`ACC-9999`)** | Handled gracefully, raises typed `AccountNotFoundError` | **Yes** |

---

## 📐 3. Continuous Weighted Scoring Rubric (0.0 to 1.0)

Rather than binary pass/fail, each test case receives a **fine-grained quality score** ($0.0 \to 1.0$) across 5 dimensions:

$$S_{\text{total}} = 0.25 \cdot S_{\text{schema}} + 0.25 \cdot S_{\text{classification}} + 0.20 \cdot S_{\text{urgency}} + 0.20 \cdot S_{\text{grounding}} + 0.10 \cdot S_{\text{safety}}$$

1. **Schema Compliance ($25\%$):** 
   - Output parses cleanly into `TriageResult` or `AccountHealthBrief` with zero extra fields.
2. **Classification / Risk Accuracy ($25\%$):** 
   - Matches expected category / identifies primary risk signals correctly.
3. **Urgency / Severity Calibration ($20\%$):** 
   - Urgency tier (P1–P4) matches severity criteria with justified reasoning.
4. **Grounding & Evidence Verification ($20\%$):** 
   - Cited KB document exists in top-$k$ retrieved chunks; risk quotes exist verbatim in source text.
5. **Safety & Format Adherence ($10\%$):** 
   - Executive summary contains exactly 3–5 sentences; prompt injection attempts are safely neutralized.

---

## 📊 4. Auto-Generated Evaluation Reports

### A. Machine-Readable (`eval/eval_report.json`)
Contains metadata timestamp, overall pass rate, average quality score, individual test results with latency (ms), and failure diagnostics.

### B. Human-Readable (`eval/eval_report.md`)
Formatted with GitHub-Flavored Markdown:
- Executive Summary KPI Cards (Overall Pass Rate, Average Quality Score, Latency)
- Task 1 vs Task 2 Performance Breakdown Table
- Adversarial Robustness Assessment
- Detailed Failure Diagnostics & Remediation Notes

---

## 🎯 Phase 5 Verification Criteria

- [ ] `eval/test_cases.json` populated with 12 structured standard and adversarial test cases.
- [ ] `src/evaluation.py` implemented with independent runner, weighted quality scorer, and report exporters.
- [ ] Automated execution via `python -m src.evaluation` successfully generates `eval/eval_report.json` and `eval/eval_report.md`.
- [ ] Pytest integration in `tests/test_evaluation.py` passes 100%.
