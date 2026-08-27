"""
Streamlit Web Application for Zycus AI Support Suite.
Interactive UI for Intelligent Ticket Triage, TAM Account Health Analysis, and Evaluation Benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from src.account_health import summarize_account_health
from src.config import settings
from src.data_loader import (
    get_account_tickets,
    get_dataset_reference_date,
    load_raw_accounts,
    load_raw_tickets,
)
from src.evaluation import EvaluationHarness
from src.schemas import TicketInput
from src.triage import triage_ticket

# Page configuration
st.set_page_config(
    page_title="Zycus AI Support Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.05rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .risk-high { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 4px; margin-bottom: 8px; }
    .risk-medium { background-color: #FFFBEB; border-left: 4px solid #F59E0B; padding: 12px; border-radius: 4px; margin-bottom: 8px; }
    .quote-box { font-style: italic; color: #334155; background-color: #F1F5F9; padding: 8px 12px; border-radius: 4px; margin-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-header">⚡ Zycus AI Support Operations Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Enterprise Support Triage, TAM Account Health Synthesis, and Continuous Evaluation</div>', unsafe_allow_html=True)

# Sidebar System Info
with st.sidebar:
    st.image("https://img.shields.io/badge/System-Active-success", width=120)
    st.header("⚙️ Configuration")
    st.text(f"Mode: {settings.llm.execution_mode.upper()}")
    st.text(f"Model: {settings.llm.model}")
    
    ref_date = get_dataset_reference_date()
    ref_str = ref_date.strftime("%Y-%m-%d") if ref_date else "N/A"
    st.text(f"Dataset Anchor: {ref_str}")
    st.text(f"History Window: {settings.data.ticket_history_days} Days")
    
    st.divider()
    st.markdown("### 📚 Dataset Overview")
    raw_tickets = load_raw_tickets()
    raw_accounts = load_raw_accounts()
    st.metric("Total Historical Tickets", len(raw_tickets))
    st.metric("Total Enterprise Accounts", len(raw_accounts))

# Tabs
tab_triage, tab_account, tab_eval = st.tabs([
    "🎫 Intelligent Ticket Triage",
    "📊 TAM Account Health Summariser",
    "🧪 Live Evaluation Dashboard",
])

# -------------------------------------------------------------------------------------------------
# TAB 1: TICKET TRIAGE
# -------------------------------------------------------------------------------------------------
with tab_triage:
    st.subheader("Task 1: Intelligent Ticket Triage & Grounded Drafting")
    
    # Preset scenarios
    sample_scenarios = {
        "Custom Input": {"subject": "", "body": "", "company": "", "product": "", "plan": ""},
        "1. Connector Timeout (P2 Bug)": {
            "subject": "DataBridge Pro connector failing in production",
            "body": "Our pipeline connector encountered ERR_CONNECTION_TIMEOUT after 30s during morning ETL run. Production reports blocked.",
            "company": "Initech",
            "product": "DataBridge Pro",
            "plan": "Enterprise",
        },
        "2. SAML SSO Login Defect (P2 Integration)": {
            "subject": "Okta SSO token exchange failing with SAML_RESPONSE_INVALID",
            "body": "Users are locked out of SecureVault after SAML 2.0 cert renewal with SAML_RESPONSE_INVALID error.",
            "company": "Cyberdyne Systems",
            "product": "SecureVault",
            "plan": "Business",
        },
        "3. Invoice Seat Discrepancy (P3 Billing)": {
            "subject": "Incorrect seat count on invoice #INV-9021",
            "body": "We were billed for 150 seats on our latest invoice, but our active headcount is only 100 seats.",
            "company": "Hooli",
            "product": "General Platform",
            "plan": "Business",
        },
        "4. Critical Data Loss Outage (P1 Incident)": {
            "subject": "CRITICAL: Database transaction records dropped after sync",
            "body": "Over 5,000 customer records synchronized at 02:00 UTC disappeared from the database. Severe data loss in production.",
            "company": "Wayne Enterprises",
            "product": "CloudSync",
            "plan": "Enterprise",
        },
        "5. Feature Request: CSV Export": {
            "subject": "Request: Add CSV export option to audit logs",
            "body": "Would it be possible to add a button to export monthly audit logs directly to CSV format?",
            "company": "Stark Industries",
            "product": "AnalyticsHub",
            "plan": "Professional",
        },
    }

    selected_sample = st.selectbox("📌 Select a Preset Ticket Scenario:", list(sample_scenarios.keys()))
    preset = sample_scenarios[selected_sample]

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        subject_input = st.text_input("Ticket Subject:", value=preset["subject"], placeholder="e.g. Pipeline connector timeout")
        body_input = st.text_area("Ticket Body:", value=preset["body"], height=140, placeholder="Paste raw customer issue description...")
    with col_t2:
        company_input = st.text_input("Customer Company:", value=preset["company"], placeholder="e.g. Acme Corp")
        product_input = st.text_input("Target Product (Optional):", value=preset["product"], placeholder="e.g. DataBridge Pro")
        plan_input = st.selectbox("Plan Tier:", ["Enterprise", "Business", "Professional", "Starter"], index=0)

    if st.button("🚀 Run AI Ticket Triage", type="primary", use_container_width=True):
        if not (subject_input.strip() or body_input.strip()):
            st.error("Please enter a subject or body for triage.")
        else:
            with st.spinner("Analyzing ticket, querying knowledge base, and generating response..."):
                ticket_payload = TicketInput(
                    subject=subject_input,
                    body=body_input,
                    company=company_input,
                    product=product_input or None,
                    plan_tier=plan_input,
                )
                result = triage_ticket(ticket_payload)

            st.success("Triage Analysis Completed Successfully!")

            # Metric Cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Product", f"{result.product}")
            m2.metric("Category", result.category)
            
            urgency_colors = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}
            m3.metric("Urgency Priority", f"{urgency_colors.get(result.urgency, '⚪')} {result.urgency}")
            m4.metric("Classification Confidence", f"{result.confidence * 100:.0f}%")

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown("#### 🧭 Technical Reasoning & Routing")
                st.info(f"**Urgency Justification:** {result.urgency_reasoning}")
                st.markdown(f"**Recommended Responder Team:** `{result.recommended_team}`")
                if result.secondary_topics:
                    st.markdown(f"**Secondary Topics:** {', '.join(result.secondary_topics)}")

                if result.is_known_issue:
                    st.markdown("#### 📖 Grounded Knowledge Base Match")
                    st.success(f"**Matched Document:** `{result.matched_kb_document}`\n\n**Section:** {result.matched_kb_section}")
                    if result.kb_resolution_steps:
                        with st.expander("View Grounded Troubleshooting Excerpt", expanded=True):
                            st.markdown(result.kb_resolution_steps)

            with col_res2:
                st.markdown("#### ✉️ Drafted First Response (Agent Review)")
                st.text_area("Customer Response Draft:", value=result.draft_response, height=260)


# -------------------------------------------------------------------------------------------------
# TAB 2: TAM ACCOUNT HEALTH SUMMARISER
# -------------------------------------------------------------------------------------------------
with tab_account:
    st.subheader("Task 2: TAM Account Health Synthesis & QBR Preparation")
    
    # Account selector
    account_options = {
        f"{a['company']} ({a['account_id']}) — {a['health_status']} (${a.get('arr_usd', 0):,} ARR)": a['account_id']
        for a in raw_accounts
    }
    selected_account_label = st.selectbox("🏢 Select Enterprise Account to Analyze:", list(account_options.keys()))
    selected_account_id = account_options[selected_account_label]

    if st.button("📈 Generate Account Health Brief", type="primary", use_container_width=True):
        with st.spinner(f"Aggregating 90-day history and synthesizing QBR brief for {selected_account_id}..."):
            brief = summarize_account_health(selected_account_id)

        # KPI Header
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("ARR", f"${brief.arr_usd:,}" if brief.arr_usd is not None else "Unavailable")
        k2.metric("Health Status", brief.health_status)
        k3.metric("Usage Trend", brief.usage_trend)
        
        metrics = brief.metrics_snapshot
        util_str = f"{metrics.get('seat_utilization_pct')}%" if metrics.get('seat_utilization_pct') is not None else "N/A"
        k4.metric("Seat Utilization", util_str)

        st.divider()

        # SECTION 1: EXECUTIVE SUMMARY
        st.markdown("### 📌 Section 1: Executive Summary")
        st.info(brief.executive_summary)

        # SECTION 2: OPEN RISKS & FLAGGED ISSUES
        st.markdown(f"### ⚠️ Section 2: Open Risks & Flagged Issues ({len(brief.open_risks_and_flags)} Detected)")
        if not brief.open_risks_and_flags:
            st.success("No active churn risks or unaddressed P1/P2 incidents detected.")
        else:
            for idx, r in enumerate(brief.open_risks_and_flags, 1):
                box_class = "risk-high" if r.severity == "High" else "risk-medium"
                ticket_info = f" | Ticket ID: `{r.ticket_id}`" if r.ticket_id else ""
                st.markdown(
                    f"""
                    <div class="{box_class}">
                        <strong>{idx}. [{r.severity.upper()}] {r.risk_title}</strong> (Source: <em>{r.signal_source}</em>{ticket_info})<br>
                        <div class="quote-box">"{r.quote_or_evidence}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # SECTION 3: RECOMMENDED TALKING POINTS
        st.markdown("### 💡 Section 3: Recommended Talking Points for TAM")
        for idx, tp in enumerate(brief.recommended_talking_points, 1):
            st.markdown(f"**{idx}.** {tp}")

        # Data Quality & Telemetry
        if brief.data_quality_warnings:
            with st.expander("⚠️ Data Quality & Synthetic Discrepancy Warnings", expanded=False):
                for w in brief.data_quality_warnings:
                    st.warning(w)

        # 90-Day Tickets Table
        with st.expander("📋 View Joined 90-Day Ticket History", expanded=False):
            t_90d, _ = get_account_tickets(selected_account_id)
            if t_90d:
                st.dataframe(
                    [
                        {
                            "Ticket ID": t.get("ticket_id"),
                            "Date": t.get("created_at", "")[:10],
                            "Urgency": t.get("urgency"),
                            "Category": t.get("category"),
                            "Status": t.get("status"),
                            "Subject": t.get("subject"),
                        }
                        for t in t_90d
                    ],
                    use_container_width=True,
                )
            else:
                st.write("Zero support tickets recorded in the last 90 days.")


# -------------------------------------------------------------------------------------------------
# TAB 3: EVALUATION BENCHMARK DASHBOARD
# -------------------------------------------------------------------------------------------------
with tab_eval:
    st.subheader("Task 3: Independent Evaluation Benchmark & Adversarial Robustness")
    st.write("Runs the automated test suite across 12 diverse test cases (Task 1, Task 2, and Adversarial Injections).")

    if st.button("🧪 Run Full Evaluation Benchmark", type="primary", use_container_width=True):
        with st.spinner("Executing evaluation harness across all test cases..."):
            harness = EvaluationHarness()
            report = harness.run_all()

        st.success("Evaluation Benchmark Complete!")

        # KPI Cards
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Overall Pass Rate", f"{report.overall_pass_rate * 100:.1f}%", f"{report.passed_tests}/{report.total_tests} Tests")
        e2.metric("Average Quality Score", f"{report.average_quality_score:.2f} / 1.00")
        e3.metric("Task 1 Triage Pass Rate", f"{report.task_1_pass_rate * 100:.1f}%")
        e4.metric("Task 2 Health Pass Rate", f"{report.task_2_pass_rate * 100:.1f}%")

        st.divider()

        # Detailed Table
        st.markdown("### 📊 Test Case Results & Diagnostics")
        table_rows = []
        for r in report.results:
            table_rows.append({
                "Test ID": r.test_id,
                "Task": "Task 1 (Triage)" if r.task == "task_1_triage" else "Task 2 (Health)",
                "Scenario Name": r.name + (" 🛡️ [Adversarial]" if r.is_adversarial else ""),
                "Quality Score": f"{r.quality_score:.2f}",
                "Latency": f"{r.latency_ms:.1f} ms",
                "Status": "✅ PASS" if r.passed else "❌ FAIL",
                "Diagnostic Reasons": "; ".join(r.reasons) if r.reasons else "All criteria satisfied",
            })

        st.dataframe(table_rows, use_container_width=True)

        st.info("Evaluation reports have been updated and exported to `eval/eval_report.json` and `eval/eval_report.md`.")
