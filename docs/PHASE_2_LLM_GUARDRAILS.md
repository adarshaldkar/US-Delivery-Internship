# 📑 PHASE 2: LLM CLIENT & VALIDATION GUARDRAILS BLUEPRINT

> **Objective:** Establish the production AI orchestration layer, multi-mode execution client (OpenAI + Dynamic Offline Engine), and strict post-processing evidence verification guardrails without hardcoded business rules.

---

## 🏗️ 1. Phase 2 Architecture Overview

```
                                  INCOMING REQUEST
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │  Execution Router   │
                               │ (Auto / LLM / Offl) │
                               └──────────┬──────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
             ┌─────────────────────┐             ┌─────────────────────┐
             │  OpenAI LLM Mode    │             │   Offline Engine    │
             │ (Structured JSON)   │             │  (Evidence-Driven)  │
             │  temp=0.0, seed=42  │             │   Zero Hardcoding   │
             └──────────┬──────────┘             └──────────┬──────────┘
                        │                                   │
                        └─────────────────┬─────────────────┘
                                          ▼
                               ┌─────────────────────┐
                               │  JSON Normalization │
                               │  & Extraction Layer │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │     GUARDRAILS      │
                               │  VALIDATION LAYER   │
                               ├─────────────────────┤
                               │ 1. Quote Verifier   │
                               │ 2. Grounding Check  │
                               │ 3. Schema & Enums   │
                               │ 4. Prompt Injection │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               VALIDATED OUTPUT SCHEMA
```

---

## 🛠️ 2. Detailed Component Specifications

### A. OpenAI Client Integration (`src/llm_client.py` -> `LLMClient`)
- **Model:** `gpt-4o-mini` (configurable via `OPENAI_MODEL` in `.env`).
- **Determinism:** `temperature=0.0`, fixed random `seed=42`.
- **Output Guarantee:** Enforces `response_format={"type": "json_object"}`.
- **Error Handling:** If API key is missing or rate limit occurs, seamlessly falls back to `DynamicOfflineEngine` without crashing.

### B. Dynamic Evidence-Driven Offline Engine (`DynamicOfflineEngine`)
To guarantee 100% CI pass rates without committing API keys, this engine provides deterministic inference based purely on retrieved data:
1. **Dynamic Product Attribution:** Uses `top_res.chunk.product` (extracted from the `# ` header in the Markdown document) or title-cases the document path. **Zero static `doc_to_prod` dictionaries.**
2. **Dynamic Confidence Score:** Derived from retrieval similarity and error-code matching ($0.0 \to 1.0$). **Zero static `0.95` constants.**
3. **Dynamic TAM Talking Points:** Synthesized dynamically from that specific account's metrics:
   - Contract renewal proximity ($<90$ days)
   - Low seat utilization ($<70\%$)
   - Recent P1 incident counts
   - Escalation notes from champions/stakeholders
4. **Honest Null-Value Handling:** Preserves `None` for missing ARR or NPS scores; renders `"Unavailable"` rather than fabricating `"Enterprise"` or `"Healthy"` defaults.

### C. Evidence Verification Guardrails (`src/validation.py`)
1. **Programmatic Verbatim Quote Verification (`verify_quote_exists`):**
   - Normalizes whitespace, quotes, and punctuation.
   - Searches whether the claimed quote exists verbatim within the raw ticket bodies or `escalation_notes`.
   - **Rejects any hallucinated or altered quote.**
2. **Grounded KB Citation Verification (`verify_kb_citation`):**
   - Verifies that any cited `matched_kb_document` was physically present in the top-$k$ retrieved candidate list.
   - **Rejects hallucinated KB file paths.**
3. **JSON Extraction & Sanitization (`extract_json_from_llm_response`):**
   - Safely strips Markdown code blocks (````json ... ````) and extracts valid JSON payloads.
4. **Prompt Injection Signal Detection (`has_prompt_injection_signals`):**
   - Flags untrusted customer override commands ("ignore previous instructions", "system prompt") to telemetry.

### D. Prompt Engineering & Versioning (`prompts/`)
- **Version Tracking:** `prompts/registry.json` tracks active versions (`v1.0.0`) and changelog.
- **Untrusted Data Isolation:** All prompt templates explicitly instruct the LLM that ticket content is untrusted data and must not override system instructions.

---

## 🧪 3. Phase 2 Verification & Test Suite

To consider Phase 2 complete, the following unit and integration tests must pass:

1. **Quote Verification Guardrail Tests:**
   - ✅ Verifies exact quote present in ticket body $\implies$ `True`
   - ✅ Verifies quote present in `escalation_notes` $\implies$ `True`
   - ❌ Rejects altered / paraphrased quote $\implies$ `False`
   - ❌ Rejects completely fabricated quote $\implies$ `False`
2. **KB Grounding Guardrail Tests:**
   - ✅ Accepts citation matching retrieved candidate $\implies$ `True`
   - ❌ Rejects citation to non-existent / non-retrieved file $\implies$ `False`
3. **Offline Engine Dynamism Tests:**
   - ✅ Product name matches retrieved KB chunk product dynamically
   - ✅ Confidence score reflects retrieval score (not static `0.95`)
   - ✅ Talking points adapt dynamically to account metrics (healthy vs. churning)
4. **JSON Extraction Robustness Tests:**
   - ✅ Parses raw JSON string
   - ✅ Parses Markdown fenced JSON (````json ... ````)
   - ✅ Parses JSON with preceding/trailing commentary

---

## 🎯 Phase 2 Completion Criteria

- [ ] `src/llm_client.py` refactored: all hardcoded maps and static talking points removed.
- [ ] `src/validation.py` active and integrated into post-inference pipeline.
- [ ] `prompts/registry.json` and prompt templates verified.
- [ ] Unit tests in `tests/test_validation.py` and `tests/test_llm_client.py` pass 100%.
