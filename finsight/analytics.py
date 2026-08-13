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


def validate_columns(df: pd.DataFrame, required: set[str]) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("The dataset is empty.")


def validate_data(df: pd.DataFrame) -> None:
    """Validate the complete onboarding funnel for backward compatibility."""
    validate_columns(df, {"customer_id", *(column for _, column in FUNNEL_STEPS)})


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
    validate_columns(df, {"customer_id"})
    rows = []
    for name, (column, definition) in METRICS.items():
        if column in df.columns:
            rows.append(
                {"metric": name, "definition": definition, "value": float(df[column].mean())}
            )
    if "spend_30d" in df.columns:
        rows.append(
            {
                "metric": "average_spend_30d",
                "definition": "Average 30-day spend per customer",
                "value": float(df["spend_30d"].mean()),
            }
        )
    if not rows:
        raise ValueError("No supported KPI fields were found after schema mapping.")
    recommended_primary = (
        "activation_rate"
        if "card_activated" in df.columns
        else "engagement_rate_30d"
        if "active_30d" in df.columns
        else rows[0]["metric"]
    )
    return AnalysisResult(
        analysis_type=AnalysisType.KPI,
        title="Available credit-card KPIs",
        summary={"customers": len(df), "recommended_primary_metric": recommended_primary},
        table=rows,
        notes=["Rates use all signed-up customers as the denominator."],
    )


def funnel_analysis(df: pd.DataFrame, filters: dict[str, str] | None = None) -> AnalysisResult:
    validate_columns(df, {"customer_id"})
    acquisition_fields = {"signed_up", "identity_verified", "card_activated"}
    early_use_fields = {"card_activated", "first_transaction", "active_30d"}
    if not (acquisition_fields <= set(df.columns) or early_use_fields <= set(df.columns)):
        raise ValueError(
            "Funnel analysis requires either the complete acquisition stages or the complete early-use stages."
        )
    available_steps = [(label, column) for label, column in FUNNEL_STEPS if column in df.columns]
    if len(available_steps) < 2:
        raise ValueError(
            "Funnel analysis requires at least two recognized sequential event fields."
        )
    view = apply_filters(df, filters)
    rows, previous = [], len(view)
    for label, column in available_steps:
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
        summary={
            "customers": len(view),
            "largest_drop_off_before": largest["step"],
            "lost_customers": largest["drop_off"],
        },
        table=rows,
        notes=["Funnel stages are sequential by construction."],
    )


def segment_analysis(
    df: pd.DataFrame, metric: str = "activation_rate", dimension: str = "device"
) -> AnalysisResult:
    allowed_dimensions = {"device", "acquisition_channel", "customer_segment"}
    if dimension not in allowed_dimensions:
        raise ValueError(f"Dimension must be one of: {', '.join(sorted(allowed_dimensions))}")
    if metric not in METRICS:
        raise ValueError(f"Unsupported metric: {metric}")
    column = METRICS[metric][0]
    validate_columns(df, {"customer_id", dimension, column})
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
        summary={
            "lowest_segment": str(table[0][dimension]),
            "lowest_rate": float(table[0]["rate"]),
        },
        table=table,
        notes=["Segment results are descriptive and do not establish causality."],
    )


def engagement_analysis(df: pd.DataFrame) -> AnalysisResult:
    required = {"customer_id", "active_30d", "transactions_30d", "spend_30d"}
    validate_columns(df, required)
    active = df["active_30d"].astype(bool)
    rows = [
        {
            "metric": "active_rate_30d",
            "definition": "Customers active within 30 days",
            "value": float(active.mean()),
            "format": "percent",
        },
        {
            "metric": "average_transactions_30d",
            "definition": "Average 30-day transactions per customer",
            "value": float(df["transactions_30d"].mean()),
            "format": "number",
        },
        {
            "metric": "average_spend_30d",
            "definition": "Average 30-day spend per customer",
            "value": float(df["spend_30d"].mean()),
            "format": "currency",
        },
        {
            "metric": "average_spend_active_30d",
            "definition": "Average 30-day spend among active customers",
            "value": float(df.loc[active, "spend_30d"].mean()) if active.any() else 0.0,
            "format": "currency",
        },
    ]
    return AnalysisResult(
        analysis_type=AnalysisType.ENGAGEMENT,
        title="Engagement & spend KPIs",
        summary={"customers": len(df), "active_customers": int(active.sum())},
        table=rows,
        notes=["This is a descriptive 30-day customer-level view."],
    )


def retention_analysis(df: pd.DataFrame) -> AnalysisResult:
    required = {"customer_id", "card_activated", "active_30d", "active_90d"}
    validate_columns(df, required)
    eligible = df[df["card_activated"].astype(bool)]
    if eligible.empty:
        raise ValueError("Retention analysis requires at least one activated cardholder.")
    rows = [
        {
            "metric": "active_rate_30d",
            "definition": "Activated cardholders active in the 30-day measurement window",
            "value": float(eligible["active_30d"].mean()),
            "format": "percent",
        },
        {
            "metric": "active_rate_90d",
            "definition": "Activated cardholders active in the 90-day measurement window",
            "value": float(eligible["active_90d"].mean()),
            "format": "percent",
        },
    ]
    summary = {
        "activated_customers": len(eligible),
        "active_rate_30d": float(eligible["active_30d"].mean()),
        "active_rate_90d": float(eligible["active_90d"].mean()),
    }
    if "reactivated_90d" in eligible.columns:
        reactivation = float(eligible["reactivated_90d"].mean())
        summary["reactivation_rate_90d"] = reactivation
        rows.append(
            {
                "metric": "reactivation_rate_90d",
                "definition": "Activated cardholders reactivated by day 90",
                "value": reactivation,
                "format": "percent",
            }
        )
    return AnalysisResult(
        analysis_type=AnalysisType.RETENTION,
        title="Retention & inactivity signals",
        summary=summary,
        table=rows,
        notes=[
            "Activity rates use activated cardholders as the denominator.",
            "The 30-day and 90-day fields are separate activity windows, not a survival curve; reactivation can make the later rate higher.",
        ],
    )


def _proportion_test(
    control_success: int, control_n: int, treatment_success: int, treatment_n: int
) -> dict:
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


def _sample_ratio_mismatch(
    control_n: int, treatment_n: int, expected_control_share: float = 0.5
) -> dict:
    """Two-sided normal approximation for a prespecified two-cell allocation ratio."""
    total = control_n + treatment_n
    expected_control = total * expected_control_share
    expected_treatment = total * (1 - expected_control_share)
    variance = total * expected_control_share * (1 - expected_control_share)
    z = (control_n - expected_control) / math.sqrt(variance) if variance else 0.0
    p_value = float(2 * norm.sf(abs(z)))
    return {
        "expected_control_share": expected_control_share,
        "observed_control_share": control_n / total,
        "expected_control_n": expected_control,
        "expected_treatment_n": expected_treatment,
        "srm_p_value": p_value,
        "srm_detected": bool(p_value < 0.01),
    }


def experiment_analysis(df: pd.DataFrame, metric: str = "activation_rate") -> AnalysisResult:
    if metric not in METRICS:
        raise ValueError(f"Unsupported experiment metric: {metric}")
    outcome = METRICS[metric][0]
    validate_columns(df, {"customer_id", "experiment_group", outcome, "active_30d"})
    control = df[df["experiment_group"] == "Control"]
    treatment = df[df["experiment_group"] == "Treatment"]
    if control.empty or treatment.empty:
        raise ValueError("Experiment requires both Control and Treatment groups.")
    stats = _proportion_test(
        int(control[outcome].sum()), len(control), int(treatment[outcome].sum()), len(treatment)
    )
    guardrail = _proportion_test(
        int(control["active_30d"].sum()),
        len(control),
        int(treatment["active_30d"].sum()),
        len(treatment),
    )
    srm = _sample_ratio_mismatch(len(control), len(treatment))
    rows = [
        {
            "group": "Control",
            "customers": len(control),
            "conversions": int(control[outcome].sum()),
            "rate": stats["control_rate"],
        },
        {
            "group": "Treatment",
            "customers": len(treatment),
            "conversions": int(treatment[outcome].sum()),
            "rate": stats["treatment_rate"],
        },
    ]
    summary = {
        **stats,
        **srm,
        "metric": metric,
        "guardrail_30d_lift": guardrail["absolute_lift"],
        "guardrail_30d_p_value": guardrail["p_value"],
    }
    return AnalysisResult(
        analysis_type=AnalysisType.EXPERIMENT,
        title=f"A/B test: {metric.replace('_', ' ')}",
        summary=summary,
        table=rows,
        notes=[
            "Two-sided two-proportion z-test; 95% unpooled confidence interval.",
            "Random assignment and a prespecified 50/50 allocation are assumed.",
            "SRM uses a two-sided normal approximation with a conservative 1% alert threshold.",
        ],
    )
