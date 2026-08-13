import json
import os
from collections.abc import Callable

import pandas as pd

from finsight.analytics import (
    define_kpis,
    engagement_analysis,
    experiment_analysis,
    funnel_analysis,
    retention_analysis,
    segment_analysis,
)
from finsight.contracts import AnalysisPlan, AnalysisResult, AnalysisType

ALLOWED_SCHEMA = {
    "metrics": [
        "verification_rate",
        "activation_rate",
        "first_transaction_rate",
        "engagement_rate_30d",
        "average_transactions_30d",
        "average_spend_30d",
        "active_rate_30d",
        "active_rate_90d",
    ],
    "dimensions": ["device", "acquisition_channel", "customer_segment"],
    "filters": ["device", "acquisition_channel", "customer_segment", "experiment_group"],
    "lifecycle_fields": [
        "signed_up",
        "identity_verified",
        "card_activated",
        "first_transaction",
        "active_30d",
        "active_90d",
        "transactions_30d",
        "spend_30d",
    ],
}

PLANNER_PROMPT = """You are FinSight's credit-card product-analytics planner. Translate one business question into exactly one bounded analysis plan.
Only use KPI definition, funnel, segmentation, engagement/spend, retention/inactivity, experiment analysis, or unsupported. Never calculate numbers. Never invent columns.
Use only this allowlist: {schema}. Choose activation_rate by default. Use filters only for explicit user constraints.
For experiment analysis, always return an empty filters list and a null dimension because the deterministic engine must compare the complete Control and Treatment groups. Do not describe treatment exposure as a filter.
If the question asks for prediction, forecasting, regression, causal analysis outside the randomized experiment, arbitrary exploration, or any unsupported capability, return analysis_type unsupported with null dimension, empty filters, and a short rationale. Do not force it into a supported workflow."""

INTERPRETER_PROMPT = """You are FinSight's product analytics interpreter. Explain the supplied deterministic result to a product manager.
Lead with the finding, cite the key numbers, state statistical/descriptive limitations, and give one bounded next step.
Never recalculate, alter, or invent a number, field, metric, segment, or data source. A next step may reference only fields and dimensions in the supplied schema allowlist. Avoid causal language unless the result is a randomized experiment.
For randomized experiments, describe lift as an estimated treatment effect under the random-assignment assumption. Always report the supplied sample-ratio-mismatch result. If SRM is detected, do not recommend rollout and tell the user to investigate assignment or logging. If SRM is not detected, say that this specific integrity check passed but does not prove randomization or overall experiment validity. Use human-readable business labels in prose, never snake_case field names.
If either experiment group has fewer than 100 customers, explicitly call the result exploratory and recommend collecting more observations or reviewing power and minimum detectable effect. Do not recommend segmenting a small experiment because that would reduce sample sizes further.
For experiments, follow the supplied deterministic decision status and report the approximate 80%-power MDE as a planning diagnostic, not a guarantee. Treat supplied segment diagnostics as directional consistency checks only: do not attach statistical significance, causal heterogeneity, or subgroup rollout claims to them. Never replace the decision status with a stronger rollout recommendation.
For retention/inactivity results, describe the 30-day and 90-day values as separate activity-window rates, not a monotonic cohort-retention or survival curve. State that reactivation can make the later activity rate higher."""


class Copilot:
    def __init__(self, model: str | None = None, client=None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.client = client
        if self.client is None and os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI

            self.client = OpenAI()

    @property
    def mode(self) -> str:
        return "OpenAI LLM" if self.client else "Deterministic demo"

    def plan(self, question: str) -> AnalysisPlan:
        if not self.client:
            return self._demo_plan(question)
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": PLANNER_PROMPT.format(schema=json.dumps(ALLOWED_SCHEMA)),
                },
                {"role": "user", "content": question},
            ],
            text_format=AnalysisPlan,
        )
        return response.output_parsed

    def run(self, df: pd.DataFrame, plan: AnalysisPlan) -> AnalysisResult:
        tools: dict[AnalysisType, Callable[[], AnalysisResult]] = {
            AnalysisType.KPI: lambda: define_kpis(df),
            AnalysisType.FUNNEL: lambda: funnel_analysis(
                df, {item.column: item.value for item in plan.filters}
            ),
            AnalysisType.SEGMENT: lambda: segment_analysis(
                df, plan.metric, plan.dimension or "device"
            ),
            AnalysisType.ENGAGEMENT: lambda: engagement_analysis(df),
            AnalysisType.RETENTION: lambda: retention_analysis(df),
            AnalysisType.EXPERIMENT: lambda: experiment_analysis(df, plan.metric),
            AnalysisType.UNSUPPORTED: lambda: AnalysisResult(
                analysis_type=AnalysisType.UNSUPPORTED,
                title="Unsupported request",
                summary={
                    "supported_workflows": [
                        "KPI definition",
                        "funnel analysis",
                        "customer segmentation",
                        "engagement and spend",
                        "retention and inactivity",
                        "A/B experiment evaluation",
                    ]
                },
                notes=[
                    "FinSight did not run an analysis because the request is outside the governed MVP scope."
                ],
            ),
        }
        try:
            return tools[plan.analysis_type]()
        except ValueError as exc:
            return AnalysisResult(
                analysis_type=AnalysisType.UNSUPPORTED,
                title="Dataset not compatible with this analysis",
                summary={"requested_workflow": plan.analysis_type.value},
                notes=[str(exc)],
            )

    def interpret(self, question: str, plan: AnalysisPlan, result: AnalysisResult) -> str:
        if not self.client:
            return self._demo_interpret(result)
        response = self.client.responses.create(
            model=self.model,
            instructions=INTERPRETER_PROMPT,
            input=json.dumps(
                {
                    "question": question,
                    "schema_allowlist": ALLOWED_SCHEMA,
                    "plan": plan.model_dump(mode="json"),
                    "result": result.model_dump(mode="json"),
                }
            ),
        )
        return response.output_text

    def answer(self, df: pd.DataFrame, question: str) -> tuple[AnalysisPlan, AnalysisResult, str]:
        plan = self.plan(question)
        result = self.run(df, plan)
        return plan, result, self.interpret(question, plan, result)

    @staticmethod
    def _demo_plan(question: str) -> AnalysisPlan:
        q = question.casefold()
        if any(
            word in q
            for word in [
                "predict",
                "forecast",
                "regression",
                "churn model",
                "machine learning",
            ]
        ):
            kind = AnalysisType.UNSUPPORTED
        elif any(
            word in q
            for word in [
                "experiment",
                "treatment",
                "control",
                "a/b",
                "work",
                "lift",
                "rollout",
                "improve",
                "redesign",
            ]
        ):
            kind = AnalysisType.EXPERIMENT
        elif any(word in q for word in ["drop", "funnel", "losing"]):
            kind = AnalysisType.FUNNEL
        elif any(word in q for word in ["retention", "inactive", "inactivity", "90-day", "90 day"]):
            kind = AnalysisType.RETENTION
        elif any(word in q for word in ["spend", "transaction frequency", "usage", "engagement"]):
            kind = AnalysisType.ENGAGEMENT
        elif any(word in q for word in ["which", "segment", "device", "channel", "lowest"]):
            kind = AnalysisType.SEGMENT
        else:
            kind = AnalysisType.KPI
        dimension = (
            "acquisition_channel"
            if "channel" in q
            else "customer_segment"
            if "segment" in q
            else "device"
        )
        return AnalysisPlan(
            analysis_type=kind,
            metric="activation_rate",
            dimension=dimension,
            filters=[],
            rationale="Offline demo routing based on bounded keywords.",
        )

    @staticmethod
    def _demo_interpret(result: AnalysisResult) -> str:
        s = result.summary
        if result.analysis_type == AnalysisType.EXPERIMENT:
            verdict = (
                "statistically significant" if s["significant"] else "not statistically significant"
            )
            srm = (
                "SRM detected; investigate assignment or logging before rollout"
                if s["srm_detected"]
                else "no SRM detected at the 1% threshold"
            )
            smallest_group = min(int(row["customers"]) for row in result.table)
            sample_guidance = (
                " Treat this as exploratory and collect more observations or review power and minimum detectable effect before slicing the experiment further."
                if smallest_group < 100
                else ""
            )
            return f"Treatment changed activation by {s['absolute_lift']:.1%} ({verdict}, p={s['p_value']:.3g}). The approximate 80%-power MDE is {s['approximate_mde_80']:.1%}. The 30-day engagement guardrail changed by {s['guardrail_30d_lift']:.1%}. The allocation check found {srm} (p={s['srm_p_value']:.3g}). Decision gate: {s['decision_status']}.{sample_guidance}"
        if result.analysis_type == AnalysisType.FUNNEL:
            return f"The largest loss occurs before {s['largest_drop_off_before']}: {s['lost_customers']:,} customers. Segment this step by device and acquisition channel next."
        if result.analysis_type == AnalysisType.SEGMENT:
            return f"{s['lowest_segment']} has the lowest observed rate at {s['lowest_rate']:.1%}. This is descriptive; investigate mix and journey differences before attributing a cause."
        if result.analysis_type == AnalysisType.ENGAGEMENT:
            return f"This dataset supports engagement and spend analysis for {s['customers']:,} customers; {s['active_customers']:,} were active within 30 days. Review the KPI table for usage and spend depth."
        if result.analysis_type == AnalysisType.RETENTION:
            return f"Among {s['activated_customers']:,} activated cardholders, activity was {s['active_rate_30d']:.1%} in the 30-day window and {s['active_rate_90d']:.1%} in the 90-day window. These are separate activity snapshots, so reactivation can raise the later rate."
        if result.analysis_type == AnalysisType.UNSUPPORTED:
            reason = (
                result.notes[0] if result.notes else "The request is outside the governed scope."
            )
            return f"FinSight did not run this analysis: {reason} Review the dataset compatibility panel for an available credit-card use case."
        primary = s["recommended_primary_metric"].replace("_", " ")
        return f"The available KPI framework covers {s['customers']:,} customers. Based on the confirmed fields, the recommended primary metric is {primary}."
