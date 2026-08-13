from finsight.contracts import AnalysisResult, AnalysisType
from finsight.copilot import Copilot


def test_demo_router_stays_in_scope():
    bot = Copilot(client=None)
    assert bot.plan("Where are users dropping off?").analysis_type == AnalysisType.FUNNEL
    assert bot.plan("Did the treatment work?").analysis_type == AnalysisType.EXPERIMENT
    assert (
        bot.plan("Did the redesigned onboarding flow improve activation?").analysis_type
        == AnalysisType.EXPERIMENT
    )
    assert bot.plan("Which device is lowest?").analysis_type == AnalysisType.SEGMENT
    assert bot.plan("How much are customers spending?").analysis_type == AnalysisType.ENGAGEMENT
    assert (
        bot.plan("How do 30-day and 90-day activity compare?").analysis_type
        == AnalysisType.RETENTION
    )
    assert bot.plan("What should we measure?").analysis_type == AnalysisType.KPI
    assert bot.plan("What should we measure?").filters == []


def test_unsupported_request_does_not_run_unrelated_analysis():
    bot = Copilot(client=None)
    plan = bot.plan("Build a churn prediction model")
    assert plan.analysis_type == AnalysisType.UNSUPPORTED


def test_demo_causal_segment_question_refuses_unsupported_causal_claim():
    result = AnalysisResult(
        analysis_type=AnalysisType.SEGMENT,
        title="Activation rate by device",
        summary={"lowest_segment": "Android", "lowest_rate": 0.6493},
    )
    answer = Copilot._demo_interpret("What caused Android customers to activate less?", result)
    assert answer.startswith("This descriptive segmentation cannot determine what caused")
    assert "outside the current MVP" in answer
    assert "meaningful" not in answer
