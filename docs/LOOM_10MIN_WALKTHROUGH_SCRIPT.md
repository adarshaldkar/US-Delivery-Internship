# 🎥 10-Minute Loom Walkthrough: Complete Word-for-Word Script & Teleprompter

> **Candidate:** Adarsh Patel  
> **Role:** AI Engineer — Product Support Intern (Zycus US Delivery)  
> **Target Duration:** 8:30 – 10:00 Minutes  
> **Email Requirement Alignment:**
> 1. How you approached the assignment (0:40 – 2:20)
> 2. The methodology/tools used (2:20 – 4:00)
> 3. Your implementation process (4:00 – 6:30)
> 4. Key decisions and outcomes (8:40 – 9:40)

---

## ⏱️ Video Timeline at a Glance

| Timestamp | Section | Visual on Screen | Primary Focus |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:40** | **Introduction** | `README.md` (Top-level) | Professional greeting, objective & roadmap |
| **0:40 – 2:20** | **1. Approach** | Directory tree & Architecture diagram | Layered design, zero hardcoding, data boundaries |
| **2:20 – 4:00** | **2. Methodology & Tools** | `src/schemas.py`, `src/config.py` | Python, Pydantic, TF-IDF + Error Boost, OpenAI/Offline |
| **4:00 – 6:30** | **3. Implementation** | `data_loader.py`, `retrieval.py`, `triage.py`, `account_health.py`, `validation.py` | Dynamic 90-day anchoring, KB chunking, quote verification |
| **6:30 – 8:40** | **Live Terminal Demo** | Integrated Terminal in VS Code | CLI help, Task 1 Triage, Task 2 Account Health, Pytest & Eval |
| **8:40 – 9:40** | **4. Decisions & Outcomes** | `DESIGN.md` in VS Code | 4 core engineering decisions & delivered outcomes |
| **9:40 – 10:00** | **Conclusion** | GitHub Repository | Closing statement & professional wrap-up |

---

## 🎬 0:00 – 0:40 | Introduction & Assignment Understanding

### 🖥️ What to show on screen:
Open [`README.md`](file:///c:/Users/shrut/Desktop/Zyron_assignment/README.md) in VS Code or browser with your webcam visible in the corner.

### 🎙️ Word-for-word spoken script:
> *"Hi everyone, I'm Adarsh Patel, and this is my walkthrough of the Zycus AI Engineer – Product Support Intern technical assessment.*
>
> *The assignment focused on building an enterprise-grade AI support operations system around three core pillars: **Intelligent Ticket Triage**, **TAM Account Health Summarization**, and an **Independent Evaluation Harness**, alongside production systems design in `DESIGN.md` and bonus interfaces.*
>
> *In this 10-minute walkthrough, I will cover four specific areas:*
> *1. How I approached the assignment from a systems engineering perspective,*
> *2. The methodology and tools I selected,*
> *3. The technical implementation process across each module, and*
> *4. The key engineering decisions and outcomes, concluding with a live terminal demonstration of the entire system.*
>
> *Let’s dive right in."*

---

## 🧠 0:40 – 2:20 | 1. How I Approached the Assignment

### 🖥️ What to show on screen:
Scroll down to the **System Architecture ASCII Diagram** in [`README.md`](file:///c:/Users/shrut/Desktop/Zyron_assignment/README.md) and highlight the clean project folder structure.

```text
data/
knowledge-base/
prompts/
src/
tests/
eval/
app.py
DESIGN.md
```

### 🎙️ Word-for-word spoken script:
> *"When approaching this assignment, my fundamental philosophy was to treat it as a **production-oriented support engineering platform**, rather than a simple script that directly feeds raw customer prompts to an LLM.*
>
> *I divided the problem into distinct, decoupled architectural layers:*
> 
> *```text
> Raw Unstructured Input
>           ↓
> Normalization & Targeted PII Scrubbing
>           ↓
> Dynamic Data Services & Reference Anchoring
>           ↓
> Hybrid Knowledge Retrieval (TF-IDF + Regex Boost)
>           ↓
> LLM Inference / Deterministic Offline Engine
>           ↓
> Programmatic Guardrails (Verbatim Quotes & KB Citations)
>           ↓
> Automated Evaluation & Regression Harness
> ```*
>
> *A core design principle across my entire approach was **avoiding brittle, hardcoded business mappings**. Instead of writing static if-else statements for products, accounts, or categories:*
> * First, products and troubleshooting docs are **dynamically discovered** from the supplied knowledge-base files.
> * Second, account-ticket relationships are **resolved dynamically** with defensive fallbacks for discrepancy warnings.
> * Third, all model-generated evidence is **programmatically verified against raw source ground truth** before any payload is returned to the user or downstream systems.*
>
> *This guarantees that the system remains extensible as new products or documentation are added."*

---

## 🛠️ 2:20 – 4:00 | 2. Methodology & Tools Used

### 🖥️ What to show on screen:
Open [`src/schemas.py`](file:///c:/Users/shrut/Desktop/Zyron_assignment/src/schemas.py) and show `TriageResult` and `AccountHealthBrief`. Then briefly show [`src/config.py`](file:///c:/Users/shrut/Desktop/Zyron_assignment/src/config.py).

### 🎙️ Word-for-word spoken script:
> *"Next, let's look at the methodology and core toolchain I used to build the platform:*
>
> * **1. Python 3.11 with Strict Typing:** Built entirely in modern Python with typed domain exceptions to guarantee runtime safety.
> * **2. Pydantic v2 Contractual Validation:** Used for all input and output boundary enforcement. As you can see in `src/schemas.py`, classes like `TriageResult` and `AccountHealthBrief` use `extra='forbid'` and custom field validators—such as strictly enforcing 3 to 5 sentences on the executive summary.
> * **3. In-Memory Hybrid Retrieval Engine:** Rather than relying on heavyweight external vector databases for a localized dataset, I implemented a lightweight, zero-dependency hybrid retrieval engine using `scikit-learn`'s `TfidfVectorizer` combined with exact regex error-code priority matching.
> * **4. OpenAI Structured JSON Integration:** In production LLM mode, the client connects to `gpt-4o-mini` with temperature zero, fixed random seed 42, and strict JSON Schema enforcement.
> * **5. Deterministic Offline Engine ($k$-NN Soft-Voting):** To ensure 100% test reproducibility, continuous integration without leaking credentials, and cost-free evaluation, I implemented a mathematical $k$-nearest neighbors soft-voting engine. It computes squared cosine similarities over historical labeled tickets to derive categories and urgencies with zero API dependencies.
> * **6. Pytest, FastAPI, and Streamlit:** Pytest provides our regression suite, FastAPI exposes clean REST endpoints, and Streamlit provides an interactive 3-tab operational dashboard."*

---

## ⚙️ 4:00 – 6:30 | 3. Implementation Process

### 🖥️ What to show on screen:
Quickly step through the key files in `src/`:
1. `src/data_loader.py`
2. `src/retrieval.py`
3. `src/triage.py`
4. `src/account_health.py`
5. `src/validation.py`

### 🎙️ Word-for-word spoken script:
> *"Now, let me walk through the five key components of the implementation process:*
>
> ### A. Dynamic Data Layer (`src/data_loader.py`)
> *First, the data services layer. Task 2 requires filtering the last 90 days of tickets. Because the supplied dataset represents historical benchmark data, I avoid hardcoding calendar dates by dynamically anchoring the reference date to `max(created_at)`—which is May 22, 2026. The 90-day window is computed backward from this reference point.*
> *For account matching, the system uses authoritative `account_id` joins, with defensive company name fallbacks and automatic logging of synthetic ID discrepancy warnings.*
>
> ### B. Hybrid Knowledge Retrieval (`src/retrieval.py`)
> *Second, retrieval. The knowledge base reader recursively scans the 10 Markdown files in `knowledge-base/`, parses heading hierarchies into discrete sections, extracts error tables, and fits a TF-IDF matrix. When a ticket contains an exact technical error code—like `ERR_CONNECTION_TIMEOUT`—it receives a deterministic similarity boost over purely semantic matches.*
>
> ### C. Task 1: Intelligent Ticket Triage (`src/triage.py`)
> *Third, the triage pipeline. Raw text is scrubbed for PII (redacting customer emails and bearer tokens while preserving error strings), retrieved against KB sections, inferred via LLM or offline engine, and validated. It returns product, product area, category, calibrated urgency P1 through P4 with reasoning, KB resolution steps, responder team, and a drafted response.*
>
> ### D. Task 2: TAM Account Health Brief (`src/account_health.py`)
> *Fourth, the account health pipeline. It joins account metadata with the dynamic 90-day ticket window, calculates seat utilization and renewal proximity, and synthesizes the exact 3-section brief: Executive Summary, Open Risks, and Talking Points.*
>
> ### E. Guardrails & Evidence Verification (`src/validation.py`)
> *Fifth, our defense against hallucinations. Generated risks are passed through `verify_quote_exists()`, which checks that every cited quote appears verbatim in the raw ticket text or escalation notes. If a quote cannot be verified, it is programmatically rejected."*

---

## 🖥️ 6:30 – 8:40 | Live Demonstration

### 🖥️ What to show on screen:
Switch to the **integrated terminal** in VS Code.

### 🎙️ Spoken script & actions:

#### 1. CLI Entry Point
> *"Let’s see the system in action using our unified CLI entry point."*

**Type & Run:**
```bash
python src/main.py --help
```
> *"As you can see, `main.py` provides clean subcommands for `triage`, `account-health`, `eval`, `ui`, and `api`."*

---

#### 2. Task 1 Live Triage Demo
**Type & Run:**
```bash
python src/main.py triage --subject "Pipeline Timeout" --body "DataBridge Pro connector timeout with ERR_CONNECTION_TIMEOUT after 30s"
```

**Explain the output on screen:**
> *"Here is the structured JSON output. Notice:*
> * *Product is correctly identified as DataBridge Pro, area Connectors.*
> * *Category is classified as Data Loss with technical urgency reasoning.*
> * *Crucially, `matched_kb_document` surfaces `troubleshooting/performance-and-integrations.md`, extracting the exact resolution table for `ERR_CONNECTION_TIMEOUT`.*
> * *And it provides a drafted, grounded first response ready for the support agent."*

---

#### 3. Task 2 Live Account Health Demo
**Type & Run:**
```bash
python src/main.py account-health --account-id ACC-3336
```

**Explain the output on screen:**
> *"Now let's run Task 2 for Omni Consumer Products (`ACC-3336`), an At-Risk enterprise account:*
> * *1. The Executive Summary is strictly 4 sentences long, synthesizing ARR, health status, and 10 tickets in the 90-day window.*
> * *2. Under Open Risks, it extracts source-backed quotes verbatim: '3 consecutive P1 tickets' and 'Decision maker considering competing vendor evaluation'.*
> * *3. Under Talking Points, it dynamically computes that contract renewal is in 89 days and seat utilization is at 91.8%."*

---

#### 4. Task 3 Automated Evaluation & Pytest Suite
**Type & Run:**
```bash
python src/main.py eval
```
> *"Running `python src/main.py eval` executes our 12 evaluation test cases, measuring schema validity, accuracy, and latency, and exports machine-readable JSON and Markdown reports."*

**Type & Run:**
```bash
pytest tests/ -v
```
> *"And running `pytest tests/ -v`, all 33 unit and integration tests execute and pass in approximately 2.5 seconds with zero failures."*

---

## 🏆 8:40 – 9:40 | 4. Key Decisions & Outcomes

### 🖥️ What to show on screen:
Open [`DESIGN.md`](file:///c:/Users/shrut/Desktop/Zyron_assignment/DESIGN.md) in VS Code.

### 🎙️ Word-for-word spoken script:
> *"To wrap up, I want to highlight four key engineering decisions documented in `DESIGN.md`:*
>
> * **1. Dynamic Discovery over Hardcoding:** We eliminated brittle static mappings. Any new product markdown file added to `knowledge-base/` is automatically indexed without changing a single line of Python code.
> * **2. Retrieval-Grounded Evidence before Generation:** Rather than asking the model to answer from memory, we pass retrieved context chunks into isolated data boundary wrappers.
> * **3. Post-Generation Verification Guardrails:** We treat LLM output as untrusted until verified against source ground truth for schema conformance, citation existence, and verbatim quotes.
> * **4. Reproducible Deterministic CI:** The offline soft-voting mode ensures that CI pipelines and grading environments pass all tests without external API dependencies or key management risks.
>
> *The final deliverable includes all core task pipelines, automated evaluation reporting, clean CLI and REST interfaces, interactive Streamlit UI, versioned prompts, and GitHub Actions CI workflow."*

---

## 🎤 9:40 – 10:00 | Conclusion & Wrap-Up

### 🖥️ What to show on screen:
Open your GitHub repository page: [**https://github.com/adarshaldkar/US-Delivery-Internship**](https://github.com/adarshaldkar/US-Delivery-Internship).

### 🎙️ Spoken script:
> *"In summary, my goal was to engineer a robust, modular, and defensible AI support platform rather than a simple proof-of-concept wrapper.*
>
> *The entire codebase is pushed to GitHub at `github.com/adarshaldkar/US-Delivery-Internship` with clean setup instructions and zero committed credentials.*
>
> *Thank you very much for your time and for reviewing my assessment. I look forward to your feedback!"*

---

## 🎯 Quick Recording Checklist

- [ ] Streamlit is running in background (`python src/main.py ui` or `http://localhost:8501`).
- [ ] VS Code is open with terminal ready.
- [ ] Test commands copy-pasted and verified:
  - `python src/main.py --help`
  - `python src/main.py triage --subject "Pipeline Timeout" --body "DataBridge Pro connector timeout with ERR_CONNECTION_TIMEOUT after 30s"`
  - `python src/main.py account-health --account-id ACC-3336`
  - `python src/main.py eval`
  - `pytest tests/ -v`
- [ ] Start recording on Loom $\to$ Follow the script $\to$ Stop at ~9:30 – 9:50!
