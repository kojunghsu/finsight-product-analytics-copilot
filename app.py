from datetime import UTC, datetime

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAIError

from finsight.audit import build_data_context
from finsight.copilot import Copilot
from finsight.schema import suggested_mappings
from finsight.synthetic import generate_onboarding_data
from finsight.use_cases import KNOWN_FIELDS, assess_compatibility, experiment_compatibility

load_dotenv()
st.set_page_config(page_title="FinSight", page_icon="📈", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --fs-navy: #0B1F33;
        --fs-navy-2: #12304A;
        --fs-teal: #00A6A6;
        --fs-emerald: #0E9F6E;
        --fs-cyan: #DDF7F5;
        --fs-ink: #152536;
        --fs-muted: #64748B;
        --fs-line: #DCE6EC;
        --fs-surface: #F6F9FB;
    }
    .stApp {
        background: linear-gradient(180deg, #F7FAFC 0%, #FFFFFF 38%);
        color: var(--fs-ink);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--fs-navy) 0%, var(--fs-navy-2) 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] * { color: #EAF4F7; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * { color: #AFC5D2; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,.08);
        border: 1px dashed rgba(255,255,255,.28);
        border-radius: 14px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
        background: #F3F7FA;
        border-radius: 11px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileName"] *,
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileSize"],
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileSize"] *,
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] div,
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small {
        color: var(--fs-navy) !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] {
        background: #FFFFFF;
        border: 1px solid #00A6A6;
        box-shadow: none;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] * {
        color: #007F83 !important;
        fill: #007F83 !important;
        stroke: #007F83 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #00B8B0, #008F91);
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,.18);
        box-shadow: 0 6px 16px rgba(0,0,0,.18);
        font-weight: 700;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(135deg, #13C9BE, #00A6A6);
        border-color: rgba(255,255,255,.34);
    }
    .fs-hero {
        position: relative;
        overflow: hidden;
        padding: 30px 34px;
        margin: 4px 0 24px;
        border-radius: 22px;
        background: linear-gradient(125deg, #071B2F 0%, #123B55 62%, #007F83 100%);
        box-shadow: 0 18px 45px rgba(11,31,51,.16);
    }
    .fs-hero:after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -70px;
        top: -150px;
        border-radius: 50%;
        background: rgba(99, 230, 218, .12);
    }
    .fs-brand-row { display: flex; align-items: center; gap: 13px; }
    .fs-mark {
        display: grid;
        place-items: center;
        width: 38px;
        height: 38px;
        border-radius: 11px;
        background: linear-gradient(145deg, #20D6C7, #00A6A6);
        color: #062437;
        box-shadow: 0 6px 16px rgba(0,166,166,.24);
    }
    .fs-mark svg {
        width: 21px;
        height: 21px;
        stroke: #062437;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
    }
    .fs-title { color: #FFFFFF; font-size: 38px; font-weight: 760; letter-spacing: -.04em; }
    .fs-subtitle { color: #C9DFE7; font-size: 16px; margin-top: 13px; max-width: 780px; }
    .fs-badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }
    .fs-badge {
        padding: 6px 10px;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 999px;
        background: rgba(255,255,255,.08);
        color: #E9FBF9;
        font-size: 12px;
        font-weight: 600;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--fs-line);
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 6px 18px rgba(15, 42, 61, .055);
    }
    [data-testid="stMetricLabel"] { color: var(--fs-muted); }
    [data-testid="stMetricValue"] { color: var(--fs-navy); letter-spacing: -.035em; }
    [data-testid="stAlert"] { border-radius: 14px; border-width: 1px; }
    [data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid var(--fs-line);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(15,42,61,.04);
        overflow: hidden;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--fs-line);
        border-radius: 14px;
        overflow: hidden;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #008F91, #00B3A7);
        color: #FFFFFF;
        border: 0;
        border-radius: 10px;
        box-shadow: 0 6px 16px rgba(0,166,166,.20);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #007E81, #009D94);
        color: #FFFFFF;
    }
    [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid var(--fs-line);
        border-radius: 16px;
        padding: 10px 14px;
    }
    [data-testid="stChatInput"] { border-color: #B8CCD5; border-radius: 14px; }
    h1, h2, h3 { color: var(--fs-navy) !important; letter-spacing: -.025em; }
    hr { border-color: var(--fs-line) !important; }
    </style>
    <div class="fs-hero">
      <div class="fs-brand-row">
        <div class="fs-mark" aria-label="FinSight analytics icon">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 19V13"></path>
            <path d="M10 19V9"></path>
            <path d="M16 19V5"></path>
            <path d="M3 8.5L8 5l4 2 7-4"></path>
            <path d="M16 3h3v3"></path>
          </svg>
        </div>
        <div class="fs-title">FinSight</div>
      </div>
      <div class="fs-subtitle">Governed product analytics for the credit-card customer lifecycle—turning business questions into reviewable evidence.</div>
      <div class="fs-badges">
        <span class="fs-badge">LLM-guided</span>
        <span class="fs-badge">Python-verified</span>
        <span class="fs-badge">Human-approved</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

DISPLAY_NAMES = {
    "metric": "Metric",
    "definition": "Definition",
    "value": "Current value",
    "step": "Onboarding stage",
    "customers": "Customers",
    "overall_conversion": "Overall conversion",
    "step_conversion": "Step conversion",
    "drop_off": "Customers lost",
    "group": "Experiment group",
    "conversions": "Activated customers",
    "rate": "Activation rate",
    "device": "Device",
    "acquisition_channel": "Acquisition channel",
    "customer_segment": "Customer segment",
}


def experiment_decision_status(summary: dict) -> str:
    """Derive a safe label when Streamlit reloads before imported analytics modules."""
    if status := summary.get("decision_status"):
        return str(status)
    if summary.get("srm_detected"):
        return "Investigate experiment integrity"
    if summary.get("significant") and summary.get("ci_95_low", 0) > 0:
        return "Candidate for phased rollout"
    return "Needs more evidence"


with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload onboarding CSV", type="csv")
    sample_size = st.select_slider(
        "Synthetic customers",
        [5_000, 10_000, 30_000, 50_000],
        value=30_000,
        disabled=uploaded is not None,
    )
    if not uploaded:
        st.caption("No uploaded data? FinSight generates a reproducible synthetic cohort.")


@st.cache_data
def sample_data(n: int) -> pd.DataFrame:
    return generate_onboarding_data(n=n)


if uploaded:
    try:
        raw_df = pd.read_csv(uploaded)
        mapping_key = f"schema_mapping::{uploaded.name}::{uploaded.size}"
        candidate_columns = [column for column in raw_df.columns if column not in KNOWN_FIELDS]
        suggested_targets = suggested_mappings(list(raw_df.columns), KNOWN_FIELDS)
        needs_mapping_review = bool(candidate_columns and suggested_targets)
        if needs_mapping_review and mapping_key not in st.session_state:
            st.warning(
                "Review how this CSV maps to FinSight's credit-card product fields. "
                "You may leave fields unmapped; unavailable analyses will be disabled."
            )
            with st.form("schema_mapping_form"):
                st.subheader("Schema Mapping Review")
                st.caption(
                    "Suggestions are conservative starting points. Confirm the business meaning of every event before applying them."
                )
                proposed = {}
                for target in sorted(suggested_targets):
                    suggestion = suggested_targets[target]
                    options = ["— Not mapped —", *candidate_columns]
                    index = options.index(suggestion) if suggestion in options else 0
                    proposed[target] = st.selectbox(
                        target.replace("_", " ").title(),
                        options,
                        index=index,
                        key=f"map::{mapping_key}::{target}",
                    )
                if st.form_submit_button("Apply selected mappings", type="primary"):
                    selected = {
                        target: source
                        for target, source in proposed.items()
                        if source != "— Not mapped —"
                    }
                    if len(set(selected.values())) != len(selected):
                        st.error("Each uploaded column can map to only one FinSight field.")
                    else:
                        st.session_state[mapping_key] = {
                            "mapping": selected,
                            "confirmed_at_utc": datetime.now(UTC).isoformat(),
                        }
                        st.rerun()
            st.stop()

        mapping_record = st.session_state.get(mapping_key, {})
        if "mapping" in mapping_record:
            mapping = mapping_record["mapping"]
            mapping_confirmed_at = mapping_record["confirmed_at_utc"]
        else:
            mapping = mapping_record
            mapping_confirmed_at = None
        df = raw_df.rename(columns={source: target for target, source in mapping.items()})
        if df.empty:
            raise ValueError("The dataset is empty.")
        if "signup_date" in df.columns:
            df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
        with st.sidebar:
            st.success("Uploaded CSV active")
            if mapping:
                st.caption(f"Confirmed schema mappings: {len(mapping)}")
        data_context = build_data_context(
            source_type="uploaded_csv",
            file_name=uploaded.name,
            file_size_bytes=uploaded.size,
            rows=len(df),
            mapping=mapping,
            confirmed_at_utc=mapping_confirmed_at,
        )
    except (ValueError, pd.errors.ParserError) as exc:
        st.error(f"This CSV cannot be analyzed: {exc}")
        st.info("Upload a CSV that follows the FinSight data contract described in README.md.")
        st.stop()
else:
    df = sample_data(sample_size)
    data_context = build_data_context(source_type="synthetic", rows=len(df))
copilot = Copilot()

compatibility = assess_compatibility(df)
experiment_status = experiment_compatibility(df)
with st.expander("Dataset compatibility", expanded=uploaded is not None):
    st.caption(
        "FinSight enables only the credit-card use cases supported by confirmed fields. "
        "A Limited or Unavailable module will not be forced into an analysis."
    )
    compatibility_table = pd.DataFrame(
        [
            {
                "Credit-card use case": item["use_case"],
                "Status": item["status"],
                "Missing required fields": ", ".join(
                    field.replace("_", " ").title() for field in item["missing_required"]
                )
                or "None",
            }
            for item in compatibility
        ]
        + [
            {
                "Credit-card use case": experiment_status["capability"],
                "Status": experiment_status["status"],
                "Missing required fields": ", ".join(
                    field.replace("_", " ").title()
                    for field in experiment_status["missing_required"]
                )
                or "None",
            }
        ]
    )
    st.dataframe(compatibility_table, width="stretch", hide_index=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(df):,}")
c2.metric(
    "Verified",
    f"{df['identity_verified'].mean():.1%}" if "identity_verified" in df else "Not available",
)
c3.metric(
    "Activated",
    f"{df['card_activated'].mean():.1%}" if "card_activated" in df else "Not available",
)
c4.metric(
    "30-day active",
    f"{df['active_30d'].mean():.1%}" if "active_30d" in df else "Not available",
)
if copilot.client:
    st.info(
        "Mode: OpenAI LLM. The model plans and interprets; calculations remain deterministic Python."
    )
else:
    st.info(
        "Mode: Deterministic demo. Add OPENAI_API_KEY to enable LLM planning and interpretation; calculations remain deterministic Python."
    )

examples = [
    "What should we measure for onboarding?",
    "Where are customers dropping off?",
    "Which device has the lowest activation?",
    "How are customers using and spending on the card?",
    "How do 30-day and 90-day activity compare?",
    "Did the redesigned onboarding flow improve activation?",
]
question = st.chat_input("Ask a product analytics question")
with st.expander("Try a demo question", expanded=question is None):
    selected = st.radio("Examples", examples, label_visibility="collapsed")
    if st.button("Run example", type="primary"):
        question = selected

if question:
    with st.chat_message("user"):
        st.write(question)
    try:
        plan, result, interpretation = copilot.answer(df, question)
        with st.chat_message("assistant"):
            st.write(interpretation)
            route_label = plan.analysis_type.value.replace("_", " ").title()
            st.caption(f"Analysis workflow: {route_label}")
            table = pd.DataFrame(result.table)
            if not table.empty:
                st.subheader(result.title)
                display_table = table.copy()
                for column in ["rate", "overall_conversion", "step_conversion"]:
                    if column in display_table.columns:
                        display_table[column] = display_table[column].map(
                            lambda value: f"{value:.1%}"
                        )
                for column in ["customers", "conversions", "drop_off"]:
                    if column in display_table.columns:
                        display_table[column] = display_table[column].map(
                            lambda value: f"{value:,}"
                        )
                if {"metric", "value"}.issubset(display_table.columns):
                    display_table["metric"] = (
                        display_table["metric"].str.replace("_", " ").str.title()
                    )
                    formats = (
                        table["format"]
                        if "format" in table.columns
                        else table["metric"].map(
                            lambda metric: "currency" if "spend" in metric else "percent"
                        )
                    )
                    display_table["value"] = [
                        f"${value:,.2f}"
                        if value_format == "currency"
                        else f"{value:,.2f}"
                        if value_format == "number"
                        else f"{value:.1%}"
                        for value, value_format in zip(table["value"], formats, strict=True)
                    ]
                    if "format" in display_table.columns:
                        display_table = display_table.drop(columns="format")
                display_table = display_table.rename(
                    columns={
                        column: DISPLAY_NAMES.get(column, column.replace("_", " ").title())
                        for column in display_table.columns
                    }
                )
                st.dataframe(display_table, width="stretch", hide_index=True)
                if result.analysis_type.value == "experiment":
                    decision_status = experiment_decision_status(result.summary)
                    if decision_status == "Candidate for phased rollout":
                        st.success(f"Decision gate: {decision_status}")
                    elif decision_status.startswith(("Do not roll out", "Investigate")):
                        st.error(f"Decision gate: {decision_status}")
                    else:
                        st.warning(f"Decision gate: {decision_status}")
                    decision_columns = st.columns(4)
                    decision_columns[0].metric(
                        "Absolute lift", f"{result.summary['absolute_lift']:.1%}"
                    )
                    decision_columns[1].metric(
                        "95% confidence interval",
                        f"{result.summary['ci_95_low']:.1%} to {result.summary['ci_95_high']:.1%}",
                    )
                    decision_columns[2].metric("p-value", f"{result.summary['p_value']:.3g}")
                    approximate_mde = result.summary.get("approximate_mde_80")
                    decision_columns[3].metric(
                        "Approx. MDE (80% power)",
                        f"{approximate_mde:.1%}" if approximate_mde is not None else "Restart app",
                    )
                    st.caption(
                        "Decision gates support analyst review; they do not authorize rollout. "
                        "MDE is an approximate planning diagnostic at 5% significance and 80% power."
                    )
                    srm_status = (
                        "Potential sample-ratio mismatch"
                        if result.summary["srm_detected"]
                        else "No sample-ratio mismatch detected"
                    )
                    srm_delta = (
                        f"Observed Control allocation: {result.summary['observed_control_share']:.1%} "
                        f"(expected {result.summary['expected_control_share']:.0%}); "
                        f"p = {result.summary['srm_p_value']:.3g}."
                    )
                    if result.summary["srm_detected"]:
                        st.error(
                            f"{srm_status}. {srm_delta} Investigate assignment or event logging before interpreting rollout readiness."
                        )
                    else:
                        st.success(f"{srm_status} at the 1% threshold. {srm_delta}")
                    segment_rows = result.summary.get("segment_diagnostics", [])
                    if segment_rows:
                        with st.expander("Directional consistency by available segments"):
                            st.caption(
                                "These breakdowns help detect inconsistent directions. They are descriptive, "
                                "not multiplicity-adjusted hypothesis tests."
                            )
                            segment_table = pd.DataFrame(segment_rows).rename(
                                columns={
                                    "dimension": "Dimension",
                                    "segment": "Segment",
                                    "control_customers": "Control customers",
                                    "treatment_customers": "Treatment customers",
                                    "control_rate": "Control rate",
                                    "treatment_rate": "Treatment rate",
                                    "absolute_lift": "Absolute lift",
                                    "sample_note": "Interpretation",
                                }
                            )
                            for rate_column in [
                                "Control rate",
                                "Treatment rate",
                                "Absolute lift",
                            ]:
                                segment_table[rate_column] = segment_table[rate_column].map(
                                    lambda value: f"{value:.1%}"
                                )
                            st.dataframe(segment_table, width="stretch", hide_index=True)
                if "rate" in table.columns:
                    category = next(
                        c for c in table.columns if c not in {"rate", "customers", "conversions"}
                    )
                    category_title = category.replace("_", " ").title()
                    if category == "group":
                        group_order = ["Control", "Treatment"]
                        upper_bound = min(
                            1.08,
                            max(0.7, float(table["rate"].max()) + 0.08),
                        )
                        base = alt.Chart(table).encode(
                            y=alt.Y(
                                "group:N",
                                sort=group_order,
                                title=None,
                                axis=alt.Axis(labelFontSize=13),
                            ),
                            x=alt.X(
                                "rate:Q",
                                scale=alt.Scale(domain=[0, upper_bound]),
                                axis=alt.Axis(format="%", grid=True, tickCount=8),
                                title="Activation rate",
                            ),
                        )
                        bars = base.mark_bar(cornerRadiusEnd=5, height=32).encode(
                            color=alt.Color(
                                "group:N",
                                sort=group_order,
                                scale=alt.Scale(
                                    domain=group_order,
                                    range=["#64748B", "#00A6A6"],
                                ),
                                legend=None,
                            ),
                            tooltip=[
                                alt.Tooltip("group:N", title="Experiment group"),
                                alt.Tooltip("customers:Q", title="Customers", format=","),
                                alt.Tooltip("conversions:Q", title="Conversions", format=","),
                                alt.Tooltip("rate:Q", title="Activation rate", format=".1%"),
                            ],
                        )
                        labels = base.mark_text(
                            align="left", baseline="middle", dx=8, fontSize=14, fontWeight="bold"
                        ).encode(text=alt.Text("rate:Q", format=".1%"))
                        st.subheader("Activation rate by experiment group")
                        st.altair_chart(
                            (bars + labels).properties(height=150),
                            width="stretch",
                        )
                    else:
                        chart_table = table.sort_values("rate").copy()
                        category_order = chart_table[category].astype(str).tolist()
                        lowest_rate = chart_table["rate"].min()
                        chart_table["highlight"] = chart_table["rate"].eq(lowest_rate)
                        upper_bound = min(1.0, max(0.7, float(chart_table["rate"].max()) + 0.08))
                        base = alt.Chart(chart_table).encode(
                            y=alt.Y(
                                f"{category}:N",
                                sort=category_order,
                                title=None,
                                axis=alt.Axis(labelFontSize=13, labelPadding=10),
                                scale=alt.Scale(paddingInner=0.42, paddingOuter=0.22),
                            ),
                            x=alt.X(
                                "rate:Q",
                                scale=alt.Scale(domain=[0, upper_bound]),
                                axis=alt.Axis(format="%", grid=True, tickCount=8),
                                title="Activation rate",
                            ),
                        )
                        bars = base.mark_bar(cornerRadiusEnd=5, height=24).encode(
                            color=alt.condition(
                                "datum.highlight",
                                alt.value("#00A6A6"),
                                alt.value("#7E9AAF"),
                            ),
                            tooltip=[
                                alt.Tooltip(f"{category}:N", title=category_title),
                                alt.Tooltip("customers:Q", title="Customers", format=","),
                                alt.Tooltip("rate:Q", title="Activation rate", format=".1%"),
                            ],
                        )
                        labels = base.mark_text(
                            align="left",
                            baseline="middle",
                            dx=8,
                            fontSize=14,
                            fontWeight="bold",
                        ).encode(text=alt.Text("rate:Q", format=".1%"))
                        st.altair_chart(
                            (bars + labels).properties(height=max(220, 72 * len(chart_table))),
                            width="stretch",
                        )
                elif "overall_conversion" in table.columns:
                    st.altair_chart(
                        alt.Chart(table)
                        .mark_bar(color="#00A6A6", cornerRadiusEnd=5, height=28)
                        .encode(
                            x=alt.X(
                                "overall_conversion:Q",
                                axis=alt.Axis(format="%"),
                                title="Overall conversion rate",
                            ),
                            y=alt.Y(
                                "step:N",
                                sort=list(table["step"]),
                                title="Onboarding stage",
                            ),
                            tooltip=[
                                alt.Tooltip("step:N", title="Onboarding stage"),
                                alt.Tooltip("customers:Q", title="Customers", format=","),
                                alt.Tooltip(
                                    "overall_conversion:Q",
                                    title="Overall conversion",
                                    format=".1%",
                                ),
                                alt.Tooltip(
                                    "step_conversion:Q",
                                    title="Step conversion",
                                    format=".1%",
                                ),
                            ],
                        )
                        .properties(height=300),
                        width="stretch",
                    )
            with st.expander("Audit trail"):
                st.json(
                    {
                        "data_context": data_context,
                        "dataset_compatibility": compatibility,
                        "experiment_compatibility": experiment_status,
                        "plan": plan.model_dump(mode="json"),
                        "result": result.model_dump(mode="json"),
                    }
                )
    except (OpenAIError, ValueError) as exc:
        st.error(f"Analysis could not run: {exc}")

st.divider()
data_source_note = (
    "Uploaded CSV active."
    if uploaded
    else "Synthetic data active; no real customer records are included in the demo."
)
st.caption(
    f"{data_source_note} FinSight supports decision preparation—not autonomous product, legal, compliance, or rollout decisions."
)
