from finsight.contracts import AnalysisType
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
    assert bot.plan("What is our 90-day retention?").analysis_type == AnalysisType.RETENTION
    assert bot.plan("What should we measure?").analysis_type == AnalysisType.KPI
    assert bot.plan("What should we measure?").filters == []


def test_unsupported_request_does_not_run_unrelated_analysis():
    bot = Copilot(client=None)
    plan = bot.plan("Build a churn prediction model")
    assert plan.analysis_type == AnalysisType.UNSUPPORTED
