import json
import streamlit as st
from dotenv import load_dotenv
from src.maintenance_ai.data_loader import load_data
from src.maintenance_ai.supervisor import SupervisorAgent

load_dotenv()
st.set_page_config(page_title="Multi-Agent Maintenance Assistant", page_icon="⚙️", layout="wide")
st.title("⚙️ Multi-Agent Industrial Maintenance System")
st.caption("Portfolio prototype | Synthetic wind-turbine data | Human-reviewed recommendations")

sensors, production, maintenance = load_data()
turbines = sorted(production["turbine_id"].unique())
turbine = st.selectbox("Select turbine", turbines, index=turbines.index("WT-03") if "WT-03" in turbines else 0)
question = st.text_input("Investigation question", f"Investigate performance and maintenance history for {turbine}")
use_llm = st.checkbox("Enable optional LLM summary (requires OPENAI_API_KEY)", value=False)

if st.button("Run investigation", type="primary"):
    with st.spinner("Supervisor is coordinating specialist agents..."):
        supervisor = SupervisorAgent(sensors, production, maintenance, use_llm=use_llm)
        report = supervisor.investigate(turbine, question)

    st.subheader("Supervisor summary")
    st.write(report["llm_summary"] or report["summary"])
    st.info(report["disclaimer"])

    perf = report["performance"]
    if "error" not in perf:
        c1, c2, c3 = st.columns(3)
        c1.metric("Actual production", f'{perf["actual_kwh"]:,.0f} kWh')
        c2.metric("Expected production", f'{perf["expected_kwh"]:,.0f} kWh')
        c3.metric("Below expected", f'{perf["below_expected_percent"]:.2f}%')

    left, middle, right = st.columns(3)
    with left:
        st.markdown("### Performance Agent")
        st.json(report["performance"])
    with middle:
        st.markdown("### Anomaly Agent")
        st.json(report["anomalies"])
    with right:
        st.markdown("### Maintenance Retrieval Agent")
        st.json(report["maintenance"])

    st.download_button(
        "Download investigation report (JSON)",
        data=json.dumps(report, indent=2, default=str),
        file_name=f"{turbine.lower()}_investigation_report.json",
        mime="application/json",
    )
