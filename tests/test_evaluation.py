"""
Unit tests for Task 3 Evaluation Harness.
"""

from src.config import settings
from src.evaluation import EvaluationHarness
from src.schemas import EvalReport


def test_evaluation_harness_run_all():
    harness = EvaluationHarness()
    report = harness.run_all()

    assert isinstance(report, EvalReport)
    assert report.total_tests >= 10
    assert report.overall_pass_rate >= 0.60
    assert report.average_quality_score >= 0.65
    assert (settings.paths.eval_dir / "eval_report.json").is_file()
    assert (settings.paths.eval_dir / "eval_report.md").is_file()
