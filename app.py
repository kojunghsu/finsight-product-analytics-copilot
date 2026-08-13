import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAIError

from finsight.analytics import validate_data
from finsight.copilot import Copilot
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
        df = pd.read_csv(uploaded)
        validate_data(df)
        if "signup_date" in df.columns:
            df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
        with st.sidebar:
            st.success("Uploaded CSV active")
    except (ValueError, pd.errors.ParserError) as exc:
        st.error(f"This CSV cannot be analyzed: {exc}")
        st.info("Upload a CSV that follows the FinSight data contract described in README.md.")
        st.stop()
else:
    df = sample_data(sample_size)
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
            st.caption(f"Routed to: {plan.analysis_type.value} · {plan.rationale}")
            table = pd.DataFrame(result.table)
            if not table.empty:
                st.dataframe(table, width="stretch", hide_index=True)
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
                st.json({"plan": plan.model_dump(mode="json"), "result": result.model_dump(mode="json")})
    except (OpenAIError, ValueError) as exc:
        st.error(f"Analysis could not run: {exc}")

st.divider()
st.caption("Synthetic data only. FinSight supports decision preparation—not autonomous product, legal, compliance, or rollout decisions.")
