import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from finsight.contracts import AnalysisResult, AnalysisType

FUNNEL_STEPS = [
    ("Signed up", "signed_up"),
    ("Identity verified", "identity_verified"),
    ("Card activated", "card_activated"),
    ("First transaction", "first_transaction"),
    ("30-day active", "active_30d"),
]

METRICS = {
    "verification_rate": ("identity_verified", "Signed-up customers who verify identity"),
    "activation_rate": ("card_activated", "Signed-up customers who activate their card"),
    "first_transaction_rate": ("first_transaction", "Signed-up customers who transact"),
    "engagement_rate_30d": ("active_30d", "Signed-up customers active within 30 days"),
}


def validate_data(df: pd.DataFrame) -> None:
    required = {column for _, column in FUNNEL_STEPS} | {
        "customer_id",
        "device",
        "acquisition_channel",
        "customer_segment",
        "experiment_group",
        "spend_30d",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("The dataset is empty.")


def apply_filters(df: pd.DataFrame, filters: dict[str, str] | None = None) -> pd.DataFrame:
    result = df.copy()
    for column, value in (filters or {}).items():
        if column not in result.columns:
            raise ValueError(f"Unknown filter column: {column}")
        result = result[result[column].astype(str).str.casefold() == str(value).casefold()]
    if result.empty:
        raise ValueError("No rows match the selected filters.")
    return result


def define_kpis(df: pd.DataFrame) -> AnalysisResult:
    validate_data(df)
    rows = []
    for name, (column, definition) in METRICS.items():
        rows.append({"metric": name, "definition": definition, "value": float(df[column].mean())})
    rows.append(
        {"metric": "average_spend_30d", "definition": "Average 30-day spend per signed-up customer", "value": float(df["spend_30d"].mean())}
    )
    return AnalysisResult(
        analysis_type=AnalysisType.KPI,
        title="Onboarding KPI framework",
        summary={"customers": len(df), "recommended_primary_metric": "activation_rate"},
        table=rows,
        notes=["Rates use all signed-up customers as the denominator."],
    )

def funnel_analysis(df: pd.DataFrame, filters: dict[str, str] | None = None) -> AnalysisResult:
    validate_data(df)
    view = apply_filters(df, filters)
    rows, previous = [], len(view)
    for label, column in FUNNEL_STEPS:
        count = int(view[column].sum())
        rows.append(
            {
                "step": label,
                "customers": count,
                "overall_conversion": count / len(view),
                "step_conversion": count / previous if previous else 0.0,
                "drop_off": previous - count if rows else 0,
            }
        )
        previous = count
    largest = max(rows[1:], key=lambda row: row["drop_off"])
    return AnalysisResult(
        analysis_type=AnalysisType.FUNNEL,
        title="Onboarding funnel",
        summary={"customers": len(view), "largest_drop_off_before": largest["step"], "lost_customers": largest["drop_off"]},
        table=rows,
        notes=["Funnel stages are sequential by construction."],
    )


def segment_analysis(df: pd.DataFrame, metric: str = "activation_rate", dimension: str = "device") -> AnalysisResult:
    validate_data(df)
    allowed_dimensions = {"device", "acquisition_channel", "customer_segment"}
    if dimension not in allowed_dimensions:
        raise ValueError(f"Dimension must be one of: {', '.join(sorted(allowed_dimensions))}")
    if metric not in METRICS:
        raise ValueError(f"Unsupported metric: {metric}")
    column = METRICS[metric][0]
    table = (
        df.groupby(dimension, observed=True)[column]
        .agg(customers="size", rate="mean")
        .reset_index()
        .sort_values("rate")
        .to_dict("records")
    )
    return AnalysisResult(
        analysis_type=AnalysisType.SEGMENT,
        title=f"{metric.replace('_', ' ').title()} by {dimension.replace('_', ' ')}",
        summary={"lowest_segment": str(table[0][dimension]), "lowest_rate": float(table[0]["rate"])},
        table=table,
        notes=["Segment results are descriptive and do not establish causality."],
    )


def _proportion_test(control_success: int, control_n: int, treatment_success: int, treatment_n: int) -> dict:
    p_c, p_t = control_success / control_n, treatment_success / treatment_n
    lift = p_t - p_c
    se_unpooled = math.sqrt(p_c * (1 - p_c) / control_n + p_t * (1 - p_t) / treatment_n)
    ci = (lift - 1.96 * se_unpooled, lift + 1.96 * se_unpooled)
    pooled = (control_success + treatment_success) / (control_n + treatment_n)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / control_n + 1 / treatment_n))
    z = lift / se_pooled if se_pooled else 0.0
    p_value = 2 * norm.sf(abs(z))
    return {
        "control_rate": p_c,
        "treatment_rate": p_t,
        "absolute_lift": lift,
        "relative_lift": lift / p_c if p_c else np.nan,
        "ci_95_low": ci[0],
        "ci_95_high": ci[1],
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
    }


def experiment_analysis(df: pd.DataFrame, metric: str = "activation_rate") -> AnalysisResult:
    validate_data(df)
    if metric not in METRICS:
        raise ValueError(f"Unsupported experiment metric: {metric}")
    outcome = METRICS[metric][0]
    control = df[df["experiment_group"] == "Control"]
    treatment = df[df["experiment_group"] == "Treatment"]
    if control.empty or treatment.empty:
        raise ValueError("Experiment requires both Control and Treatment groups.")
    stats = _proportion_test(int(control[outcome].sum()), len(control), int(treatment[outcome].sum()), len(treatment))
    guardrail = _proportion_test(int(control["active_30d"].sum()), len(control), int(treatment["active_30d"].sum()), len(treatment))
    rows = [
        {"group": "Control", "customers": len(control), "conversions": int(control[outcome].sum()), "rate": stats["control_rate"]},
        {"group": "Treatment", "customers": len(treatment), "conversions": int(treatment[outcome].sum()), "rate": stats["treatment_rate"]},
    ]
    summary = {**stats, "metric": metric, "guardrail_30d_lift": guardrail["absolute_lift"], "guardrail_30d_p_value": guardrail["p_value"]}
    return AnalysisResult(
        analysis_type=AnalysisType.EXPERIMENT,
        title=f"A/B test: {metric.replace('_', ' ')}",
        summary=summary,
        table=rows,
        notes=["Two-sided two-proportion z-test; 95% unpooled confidence interval.", "Random assignment is assumed; sample-ratio mismatch is not tested in this MVP."],
    )
