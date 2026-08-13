from datetime import UTC, datetime

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAIError

from finsight.analytics import REQUIRED_COLUMNS, validate_data
from finsight.audit import build_data_context
from finsight.copilot import Copilot
from finsight.schema import suggest_mapping
from finsight.synthetic import generate_onboarding_data

load_dotenv()
st.set_page_config(page_title="FinSight", page_icon="📈", layout="wide")
st.title("FinSight")
st.caption("LLM-powered product analytics copilot for digital-banking onboarding")

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
        missing = sorted(REQUIRED_COLUMNS - set(raw_df.columns))
        if missing and mapping_key not in st.session_state:
            st.warning(
                "This CSV uses a different schema. Review the suggested mappings before analysis."
            )
            candidate_columns = [
                column for column in raw_df.columns if column not in REQUIRED_COLUMNS
            ]
            with st.form("schema_mapping_form"):
                st.subheader("Schema Mapping Review")
                st.caption(
                    "Suggestions are conservative starting points. Confirm the business meaning of every event before applying them."
                )
                proposed = {}
                for target in missing:
                    suggestion = suggest_mapping(target, candidate_columns)
                    options = ["— Not mapped —", *candidate_columns]
                    index = options.index(suggestion) if suggestion in options else 0
                    proposed[target] = st.selectbox(
                        target.replace("_", " ").title(),
                        options,
                        index=index,
                        key=f"map::{mapping_key}::{target}",
                    )
                if st.form_submit_button("Apply confirmed mapping", type="primary"):
                    selected = {
                        target: source
                        for target, source in proposed.items()
                        if source != "— Not mapped —"
                    }
                    if len(selected) != len(missing):
                        st.error("Map every required field before continuing.")
                    elif len(set(selected.values())) != len(selected):
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
        validate_data(df)
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

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(df):,}")
c2.metric("Verified", f"{df.identity_verified.mean():.1%}")
c3.metric("Activated", f"{df.card_activated.mean():.1%}")
c4.metric("30-day active", f"{df.active_30d.mean():.1%}")
if copilot.client:
    st.info("Mode: OpenAI LLM. The model plans and interprets; calculations remain deterministic Python.")
else:
    st.info("Mode: Deterministic demo. Add OPENAI_API_KEY to enable LLM planning and interpretation; calculations remain deterministic Python.")

examples = [
    "What should we measure for onboarding?",
    "Where are customers dropping off?",
    "Which device has the lowest activation?",
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
                display_table = table.copy()
                for column in ["rate", "overall_conversion", "step_conversion"]:
                    if column in display_table.columns:
                        display_table[column] = display_table[column].map(lambda value: f"{value:.1%}")
                for column in ["customers", "conversions", "drop_off"]:
                    if column in display_table.columns:
                        display_table[column] = display_table[column].map(lambda value: f"{value:,}")
                if {"metric", "value"}.issubset(display_table.columns):
                    display_table["metric"] = display_table["metric"].str.replace("_", " ").str.title()
                    display_table["value"] = [
                        f"${value:,.2f}" if metric == "average_spend_30d" else f"{value:.1%}"
                        for metric, value in zip(table["metric"], table["value"], strict=True)
                    ]
                display_table = display_table.rename(
                    columns={column: column.replace("_", " ").title() for column in display_table.columns}
                )
                st.dataframe(display_table, width="stretch", hide_index=True)
                if "rate" in table.columns:
                    category = next(c for c in table.columns if c not in {"rate", "customers", "conversions"})
                    category_title = category.replace("_", " ").title()
                    if category == "group":
                        group_order = ["Control", "Treatment"]
                        base = alt.Chart(table).encode(
                            y=alt.Y(
                                "group:N",
                                sort=group_order,
                                title=None,
                                axis=alt.Axis(labelFontSize=13),
                            ),
                            x=alt.X(
                                "rate:Q",
                                scale=alt.Scale(domain=[0, 0.7]),
                                axis=alt.Axis(format="%"),
                                title="Activation rate",
                            ),
                        )
                        bars = base.mark_bar(cornerRadiusEnd=5, height=32).encode(
                            color=alt.Color(
                                "group:N",
                                sort=group_order,
                                scale=alt.Scale(
                                    domain=group_order,
                                    range=["#64748B", "#FF4B4B"],
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
                        st.altair_chart(
                            alt.Chart(table)
                            .mark_bar()
                            .encode(
                                x=alt.X(f"{category}:N", sort="-y", title=category_title),
                                y=alt.Y(
                                    "rate:Q",
                                    axis=alt.Axis(format="%"),
                                    title="Activation rate",
                                ),
                                tooltip=list(table.columns),
                            )
                            .properties(height=300),
                            width="stretch",
                        )
                elif "overall_conversion" in table.columns:
                    st.altair_chart(
                        alt.Chart(table)
                        .mark_bar()
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
