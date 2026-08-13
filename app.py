import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from finsight.copilot import Copilot
from finsight.synthetic import generate_onboarding_data

load_dotenv()
st.set_page_config(page_title="FinSight", page_icon="📈", layout="wide")
st.title("FinSight")
st.caption("LLM-powered product analytics copilot for digital-banking onboarding")

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload onboarding CSV", type="csv")
    sample_size = st.select_slider("Synthetic customers", [5_000, 10_000, 30_000, 50_000], value=30_000)
    st.caption("No uploaded data? FinSight generates a reproducible synthetic cohort.")

@st.cache_data
def sample_data(n: int) -> pd.DataFrame:
    return generate_onboarding_data(n=n)

df = pd.read_csv(uploaded, parse_dates=["signup_date"]) if uploaded else sample_data(sample_size)
copilot = Copilot()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(df):,}")
c2.metric("Verified", f"{df.identity_verified.mean():.1%}")
c3.metric("Activated", f"{df.card_activated.mean():.1%}")
c4.metric("30-day active", f"{df.active_30d.mean():.1%}")
st.info(f"Mode: {copilot.mode}. Add OPENAI_API_KEY to enable LLM planning and interpretation; calculations always remain deterministic Python.")

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
                st.dataframe(table, use_container_width=True, hide_index=True)
                if "rate" in table.columns:
                    category = next(c for c in table.columns if c not in {"rate", "customers", "conversions"})
                    st.altair_chart(alt.Chart(table).mark_bar().encode(x=alt.X(f"{category}:N", sort="-y"), y=alt.Y("rate:Q", axis=alt.Axis(format="%")), tooltip=list(table.columns)).properties(height=300), use_container_width=True)
                elif "overall_conversion" in table.columns:
                    st.altair_chart(alt.Chart(table).mark_bar().encode(x=alt.X("step:N", sort=None), y=alt.Y("overall_conversion:Q", axis=alt.Axis(format="%")), tooltip=list(table.columns)).properties(height=300), use_container_width=True)
            with st.expander("Audit trail"):
                st.json({"plan": plan.model_dump(mode="json"), "result": result.model_dump(mode="json")})
    except Exception as exc:
        st.error(f"Analysis could not run: {exc}")

st.divider()
st.caption("Synthetic data only. FinSight supports decision preparation—not autonomous product, legal, compliance, or rollout decisions.")
