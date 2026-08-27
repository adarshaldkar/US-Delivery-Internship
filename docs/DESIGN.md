# 📐 Production Architecture & Design Note
**Zycus AI Support Suite — Technical Systems Engineering**

---

## 1. Failure Modes & Cascading Risk

In an enterprise AI support infrastructure, classification and retrieval failures do not occur in isolation—they trigger compounding operational failures across downstream systems:

```
[ Misclassification / Retrieval Miss ]
                │
        ┌───────┴───────┐
        ▼               ▼
[ False Route ]  [ SLA Breach ]
        │               │
        └───────┬───────┘
                ▼
   [ Executive Churn Risk ]
```

* **Silent KB Retrieval Misses & Hallucinated Fixes:** If semantic search fails on a novel error code, an ungrounded LLM may hallucinate configuration steps, leading to extended customer downtime. We mitigate this with **Strict Grounding Guardrails**: if retrieval confidence falls below $0.25$, the system explicitly sets `is_known_issue: false`, clears `matched_kb_document`, and flags the case for human investigation.
* **Urgency Misclassification & SLA Breaches:** Downgrading a critical database corruption event from P1 to P3 breaches enterprise response SLAs and triggers contractual financial penalties. We enforce deterministic override rules on catastrophic data loss signals and maintain a secondary sentiment/churn detector that escalates ambiguous cases to human lead triage.
* **Telemetry & Drift Detection:** Every inference logs model confidence, token latency, retrieval cosine scores, and user override feedback into partitioned observability sinks to trigger automated retraining when concept drift exceeds statistical thresholds.

---

## 2. Latency vs. Quality Trade-offs

Production triage requires a tiered architecture balancing instant edge response with deep reasoning:

```
                          INCOMING TICKET
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ Fast-Path Tier-1 ]            [ Deep Reasoning Tier-2 ]
       • Exact Regex Match             • Multi-Topic Decomposition
       • TF-IDF Error Boost            • Grounded First-Response Draft
       • SLA: < 15ms                   • SLA: < 1200ms
```

* **Synchronous Low-Latency Path ($<25\text{ms}$):** Initial ticket ingestion, PII redaction, exact error-code matching, and team routing execute on lightweight in-memory TF-IDF indices. This guarantees instant webhook dispatch and immediate SLA acknowledgment to the customer portal.
* **Asynchronous Deep Reasoning ($1–2\text{s}$):** Multi-topic decomposition, root-cause synthesis, and empathetic draft generation run asynchronously via `gpt-4o-mini` with structured JSON output formatting.
* **Model Tiering Strategy:** Routine L1 inquiries (e.g., password reset, known error codes) are resolved deterministically via cached KB resolution snippets at $0\text{ms}$ LLM cost. Ambiguous, high-ARR customer escalations invoke full structured LLM reasoning.

---

## 3. Sensitive Customer Data & External API Security

Enterprise support payloads frequently contain sensitive authentication tokens, database connection strings, customer emails, and PII:

```
Raw Customer Ticket ──► [ Targeted PII Redaction ] ──► [ Untrusted Data Wrapper ] ──► External LLM
(Emails, JWTs, IPs)      (Preserves Error Codes)        (System Prompt Shield)         (Zero Retention)
```

* **In-Flight Targeted Token Scrubbing:** Before any string is transmitted to external model endpoints, `src/normalization.py` applies deterministic regex masking across emails (`[REDACTED_EMAIL]`), JWT bearer tokens (`[REDACTED_TOKEN]`), credit card PANs (`[REDACTED_CARD]`), and phone numbers (`[REDACTED_PHONE]`). Crucially, technical error tokens (e.g. `ERR_CONNECTION_TIMEOUT`) are strictly preserved.
* **Zero-Data-Retention & Tenant Isolation:** API requests use enterprise OpenAI endpoints with Zero Data Retention (ZDR) agreements, ensuring customer support snippets are never used for model training.
* **Untrusted Customer Data Shielding:** Ticket text is treated as untrusted payload, isolated within explicit data boundary tags in prompt templates to prevent prompt injection and system prompt extraction.

---

## 4. Scaling to 10× Volume (5,000+ Tickets / Day)

To scale seamlessly from 500 tickets to 5,000+ daily tickets across 500+ global enterprise accounts:

```
[ API Gateway / Ingestion ]
            │
            ▼
 [ Apache Kafka / RabbitMQ ] ──► [ Distributed Celery Workers ]
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                               ▼                               ▼
     [ Redis Semantic Cache ]        [ Qdrant Vector DB ]            [ PostgreSQL Replica ]
      (Cached Top-100 FAQs)          (HNSW Chunk Search)              (90-Day Account Joins)
```

1. **Decoupled Asynchronous Processing:** An API gateway writes incoming tickets into an Apache Kafka message queue. A cluster of auto-scaling Celery workers consumes the queue, isolating burst traffic from LLM rate limits.
2. **Semantic Caching Layer:** A distributed Redis cache stores vector embeddings of verified FAQ resolutions. Repetitive known issues are answered in $<5\text{ms}$ without invoking external LLMs.
3. **Dedicated Vector Database:** The in-memory TF-IDF retriever transitions to a distributed Qdrant or Pinecone cluster with HNSW indexing, enabling sub-millisecond similarity search across 100,000+ documentation sections.
4. **Database Read-Replicas:** Account metadata and 90-day ticket history queries execute against read-only database replicas with compound indexing on `(account_id, created_at)`, keeping QBR synthesis off the primary transaction database.
