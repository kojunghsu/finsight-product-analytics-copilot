import json
import os
from typing import Callable

import pandas as pd

from finsight.analytics import define_kpis, experiment_analysis, funnel_analysis, segment_analysis
from finsight.contracts import AnalysisPlan, AnalysisResult, AnalysisType

ALLOWED_SCHEMA = {
    "metrics": ["verification_rate", "activation_rate", "first_transaction_rate", "engagement_rate_30d"],
    "dimensions": ["device", "acquisition_channel", "customer_segment"],
    "filters": ["device", "acquisition_channel", "customer_segment", "experiment_group"],
}

PLANNER_PROMPT = """You are FinSight's product-analytics planner. Translate one business question into exactly one bounded analysis plan.
Only use KPI definition, funnel, segmentation, or experiment analysis. Never calculate numbers. Never invent columns.
Use only this allowlist: {schema}. Choose activation_rate by default. Use filters only for explicit user constraints."""

INTERPRETER_PROMPT = """You are FinSight's product analytics interpreter. Explain the supplied deterministic result to a product manager.
Lead with the finding, cite the key numbers, state statistical/descriptive limitations, and give one bounded next step.
Never recalculate, alter, or invent a number. Avoid causal language unless the result is a randomized experiment."""


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
                {"role": "system", "content": PLANNER_PROMPT.format(schema=json.dumps(ALLOWED_SCHEMA))},
                {"role": "user", "content": question},
            ],
            text_format=AnalysisPlan,
        )
        return response.output_parsed

    def run(self, df: pd.DataFrame, plan: AnalysisPlan) -> AnalysisResult:
        tools: dict[AnalysisType, Callable[[], AnalysisResult]] = {
            AnalysisType.KPI: lambda: define_kpis(df),
            AnalysisType.FUNNEL: lambda: funnel_analysis(df, plan.filters),
            AnalysisType.SEGMENT: lambda: segment_analysis(df, plan.metric, plan.dimension or "device"),
            AnalysisType.EXPERIMENT: lambda: experiment_analysis(df, plan.metric),
        }
        return tools[plan.analysis_type]()

    def interpret(self, question: str, plan: AnalysisPlan, result: AnalysisResult) -> str:
        if not self.client:
            return self._demo_interpret(result)
        response = self.client.responses.create(
            model=self.model,
            instructions=INTERPRETER_PROMPT,
            input=json.dumps({"question": question, "plan": plan.model_dump(mode="json"), "result": result.model_dump(mode="json")}),
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
        elif any(word in q for word in ["which", "segment", "device", "channel", "lowest"]):
            kind = AnalysisType.SEGMENT
        else:
            kind = AnalysisType.KPI
        dimension = "acquisition_channel" if "channel" in q else "customer_segment" if "segment" in q else "device"
        return AnalysisPlan(analysis_type=kind, metric="activation_rate", dimension=dimension, rationale="Offline demo routing based on bounded keywords.")

    @staticmethod
    def _demo_interpret(result: AnalysisResult) -> str:
        s = result.summary
        if result.analysis_type == AnalysisType.EXPERIMENT:
            verdict = "statistically significant" if s["significant"] else "not statistically significant"
            return f"Treatment changed activation by {s['absolute_lift']:.1%} ({verdict}, p={s['p_value']:.3g}). The 30-day engagement guardrail changed by {s['guardrail_30d_lift']:.1%}. Review operational and compliance constraints before rollout."
        if result.analysis_type == AnalysisType.FUNNEL:
            return f"The largest loss occurs before {s['largest_drop_off_before']}: {s['lost_customers']:,} customers. Segment this step by device and acquisition channel next."
        if result.analysis_type == AnalysisType.SEGMENT:
            return f"{s['lowest_segment']} has the lowest observed rate at {s['lowest_rate']:.1%}. This is descriptive; investigate mix and journey differences before attributing a cause."
        return f"The KPI framework covers {s['customers']:,} customers and uses activation rate as the primary onboarding outcome, supported by verification, first-transaction, and 30-day engagement metrics."
