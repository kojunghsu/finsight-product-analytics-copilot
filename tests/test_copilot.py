from finsight.contracts import AnalysisType
from finsight.copilot import Copilot


def test_demo_router_stays_in_scope():
    bot = Copilot(client=None)
    assert bot.plan("Where are users dropping off?").analysis_type == AnalysisType.FUNNEL
    assert bot.plan("Did the treatment work?").analysis_type == AnalysisType.EXPERIMENT
    assert bot.plan("Did the redesigned onboarding flow improve activation?").analysis_type == AnalysisType.EXPERIMENT
    assert bot.plan("Which device is lowest?").analysis_type == AnalysisType.SEGMENT
    assert bot.plan("What should we measure?").analysis_type == AnalysisType.KPI
