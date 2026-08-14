from finsight.contracts import AnalysisPlan, AnalysisResult, AnalysisType
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


def test_unsupported_dataset_message_uses_business_labels():
    result = AnalysisResult(
        analysis_type=AnalysisType.UNSUPPORTED,
        title="Dataset not compatible with this analysis",
        summary={},
        notes=["Missing required columns: active_30d, customer_id"],
    )
    answer = Copilot._unsupported_interpret(result)
    assert "Active 30D" in answer
    assert "Customer ID" in answer
    assert "active_30d" not in answer
    assert "customer_id" not in answer
    assert "No KPI" in answer
    assert "Customer ID. No KPI" in answer


def test_explicit_retention_intent_overrides_neighboring_llm_route():
    wrong_plan = AnalysisPlan(
        analysis_type=AnalysisType.KPI,
        metric="activation_rate",
        dimension="device",
        filters=[],
        rationale="Incorrect neighboring workflow.",
    )
    plan = Copilot._enforce_explicit_intent(
        "How do 30-day and 90-day customer activity compare?", wrong_plan
    )
    assert plan.analysis_type == AnalysisType.RETENTION
    assert plan.metric == "active_rate_90d"
    assert plan.dimension is None


def test_explicit_kpi_intent_overrides_neighboring_llm_route():
    wrong_plan = AnalysisPlan(
        analysis_type=AnalysisType.FUNNEL,
        metric="activation_rate",
        dimension=None,
        filters=[],
        rationale="Incorrect neighboring workflow.",
    )
    plan = Copilot._enforce_explicit_intent(
        "What should we measure for onboarding?", wrong_plan
    )
    assert plan.analysis_type == AnalysisType.KPI
    assert plan.metric == "activation_rate"


def test_demo_causal_segment_question_refuses_unsupported_causal_claim():
    result = AnalysisResult(
        analysis_type=AnalysisType.SEGMENT,
        title="Activation rate by device",
        summary={"lowest_segment": "Android", "lowest_rate": 0.6493},
        table=[
            {"device": "Android", "customers": 134, "rate": 0.6493},
            {"device": "iOS", "customers": 134, "rate": 0.6493},
            {"device": "Web", "customers": 132, "rate": 0.6515},
        ],
    )
    plan = Copilot(client=None).plan("What caused Android customers to activate less?")
    answer = Copilot(client=None).interpret(
        "What caused Android customers to activate less?", plan, result
    )
    assert answer.startswith("This analysis cannot determine what caused")
    assert "outside the current MVP" in answer
    assert "meaningful" not in answer
    assert "Android: 64.9% (134 customers)" in answer
    assert "0.6493" not in answer
    assert "within device" not in answer
    assert "compare overall activation by acquisition channel or customer segment" in answer
