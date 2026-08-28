"""Independent evaluation harness for Tasks 1 and 2."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

from src.account_health import summarize_account_health
from src.config import settings
from src.data_loader import load_raw_accounts, load_raw_tickets
from src.exceptions import AccountNotFoundError
from src.schemas import EvalReport, SingleEvalResult, TestCase, AccountHealthBrief
from src.triage import triage_ticket


def _ticket_cases() -> list[TestCase]:
    tickets_map = {t["ticket_id"]: t for t in load_raw_tickets()}
    representative_ids = ["TKT-10000", "TKT-10001", "TKT-10003", "TKT-10009", "TKT-10033"]
    cases: list[TestCase] = []

    for idx, t_id in enumerate(representative_ids, 1):
        ticket = tickets_map.get(t_id)
        if not ticket:
            continue
        category = ticket.get("category")
        cases.append(
            TestCase(
                test_id=f"T1-{idx}",
                task="task_1_triage",
                name=f"Representative {category} ticket",
                input_data={
                    "subject": ticket.get("subject"),
                    "body": ticket.get("body"),
                    "product": ticket.get("product"),
                },
                expected_criteria={
                    "product": ticket.get("product"),
                    "category": category,
                    "urgency": ticket.get("urgency"),
                },
            )
        )

    cases.append(
        TestCase(
            test_id="T1-ADV-EMPTY",
            task="task_1_triage",
            name="Empty ticket",
            is_adversarial=True,
            input_data={"subject": "", "body": ""},
            expected_criteria={"error": "INVALID_TICKET"},
        )
    )
    return cases


def _account_cases() -> list[TestCase]:
    accounts = list(load_raw_accounts())
    cases: list[TestCase] = []
    seen: set[str] = set()

    for account in accounts:
        health = account.get("health_status")
        if health in seen:
            continue
        seen.add(health)
        cases.append(
            TestCase(
                test_id=f"T2-{len(cases) + 1}",
                task="task_2_account_health",
                name=f"Representative {health} account",
                input_data={"account_id": account.get("account_id")},
                expected_criteria={"account_id": account.get("account_id")},
            )
        )
        if len(cases) == 4:
            break

    cases.append(
        TestCase(
            test_id="T2-ADV-UNKNOWN",
            task="task_2_account_health",
            name="Unknown account ID",
            is_adversarial=True,
            input_data={"account_id": "ACC-DOES-NOT-EXIST"},
            expected_criteria={"error": "ACCOUNT_NOT_FOUND"},
        )
    )
    return cases


def build_test_cases() -> list[TestCase]:
    return _ticket_cases() + _account_cases()


def _sentence_count(value: str) -> int:
    return len([x for x in re.split(r"(?<=[.!?])\s+", value.strip()) if x])


def _score_triage(result: dict, expected: dict) -> tuple[bool, float, list[str]]:
    reasons: list[str] = []
    checks: list[bool] = []

    for field in ("product", "category", "urgency"):
        if field == "category":
            ok = (
                result.get(field) == expected.get(field)
                or expected.get(field) in (result.get("secondary_topics") or [])
            )
        else:
            ok = result.get(field) == expected.get(field)
        checks.append(ok)
        if not ok:
            reasons.append(
                f"{field}: expected {expected.get(field)!r}, got {result.get(field)!r}"
            )

    checks.extend([
        bool(result.get("recommended_team")),
        bool(result.get("draft_response")),
        0.0 <= result.get("confidence", -1) <= 1.0,
    ])

    score = sum(checks) / len(checks)
    return all(checks), round(score, 3), reasons


def _score_account(
    result: AccountHealthBrief,
    expected: dict,
) -> tuple[bool, float, list[str]]:
    reasons: list[str] = []
    output = result.model_dump()

    checks = [
        output.get("account_id") == expected.get("account_id"),
        3 <= _sentence_count(output["executive_summary"]) <= 5,
        "open_risks_and_flags" in output,
        "recommended_talking_points" in output,
        bool(output["recommended_talking_points"]),
    ]

    if not all(checks):
        reasons.append("Account-health structural requirement failed.")

    for risk in result.open_risks_and_flags:
        if not risk.quote_or_evidence.strip():
            checks.append(False)
            reasons.append(f"Empty evidence: {risk.risk_title}")
        else:
            checks.append(True)

    score = sum(checks) / len(checks)
    return all(checks), round(score, 3), reasons


def run_evaluation() -> EvalReport:
    results: list[SingleEvalResult] = []

    for case in build_test_cases():
        started = time.perf_counter()

        try:
            if case.task == "task_1_triage":
                if case.is_adversarial:
                    try:
                        triage_ticket(case.input_data)
                    except ValueError:
                        output = {"error": "INVALID_TICKET"}
                        passed, score, reasons = True, 1.0, []
                    else:
                        output = {"error": "expected INVALID_TICKET"}
                        passed, score, reasons = False, 0.0, [
                            "Empty ticket was accepted."
                        ]
                else:
                    result = triage_ticket(case.input_data)
                    output = result.model_dump()
                    passed, score, reasons = _score_triage(
                        output, case.expected_criteria
                    )

            else:
                if case.is_adversarial:
                    try:
                        summarize_account_health(case.input_data["account_id"])
                    except AccountNotFoundError:
                        output = {"error": "ACCOUNT_NOT_FOUND"}
                        passed, score, reasons = True, 1.0, []
                    else:
                        output = {"error": "expected ACCOUNT_NOT_FOUND"}
                        passed, score, reasons = False, 0.0, [
                            "Unknown account was accepted."
                        ]
                else:
                    result = summarize_account_health(
                        case.input_data["account_id"]
                    )
                    output = result.model_dump()
                    passed, score, reasons = _score_account(
                        result,
                        case.expected_criteria,
                    )

        except Exception as exc:
            output = {"error": type(exc).__name__, "message": str(exc)}
            passed, score, reasons = False, 0.0, [
                f"Unexpected failure: {type(exc).__name__}: {exc}"
            ]

        latency = (time.perf_counter() - started) * 1000
        results.append(
            SingleEvalResult(
                test_id=case.test_id,
                task=case.task,
                name=case.name,
                is_adversarial=case.is_adversarial,
                passed=passed,
                quality_score=score,
                reasons=reasons,
                actual_output=output,
                latency_ms=round(latency, 3),
            )
        )

    total = len(results)
    passed_total = sum(item.passed for item in results)
    task1 = [item for item in results if item.task == "task_1_triage"]
    task2 = [item for item in results if item.task == "task_2_account_health"]

    report = EvalReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_tests=total,
        passed_tests=passed_total,
        failed_tests=total - passed_total,
        overall_pass_rate=passed_total / total if total else 0.0,
        average_quality_score=(
            sum(item.quality_score for item in results) / total
            if total else 0.0
        ),
        task_1_pass_rate=(
            sum(item.passed for item in task1) / len(task1)
            if task1 else 0.0
        ),
        task_2_pass_rate=(
            sum(item.passed for item in task2) / len(task2)
            if task2 else 0.0
        ),
        results=results,
    )

    settings.paths.eval_dir.mkdir(parents=True, exist_ok=True)
    (settings.paths.eval_dir / "eval_report.json").write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Evaluation Report",
        "",
        f"- Total: {report.total_tests}",
        f"- Passed: {report.passed_tests}",
        f"- Failed: {report.failed_tests}",
        f"- Overall pass rate: {report.overall_pass_rate:.1%}",
        f"- Average quality: {report.average_quality_score:.3f}",
        f"- Task 1 pass rate: {report.task_1_pass_rate:.1%}",
        f"- Task 2 pass rate: {report.task_2_pass_rate:.1%}",
        "",
    ]

    for result in report.results:
        lines.extend([
            f"## {result.test_id} — {result.name}",
            f"- Passed: {result.passed}",
            f"- Quality: {result.quality_score:.3f}",
            f"- Latency: {result.latency_ms:.1f} ms",
        ])
        for reason in result.reasons:
            lines.append(f"- Note: {reason}")
        lines.append("")

    (settings.paths.eval_dir / "eval_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
    return report


class EvaluationHarness:
    """Wrapper class for running full evaluation harness."""

    def __init__(self, *args, **kwargs):
        pass

    def run_all(self) -> EvalReport:
        return run_evaluation()

