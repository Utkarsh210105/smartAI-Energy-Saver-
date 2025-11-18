import streamlit as st
import os
import tempfile
import pandas as pd
import numpy as np

from forecast import run_forecast
from generate_tips import run_tips
from yearly_analysis import plot_year_comparison, plot_year_averages
from report_generator import generate_pdf_report
from utils import DATA_DIR, FORECAST_DIR, read_csv

# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(page_title="Eco Electricity Dashboard", layout="wide")

# ------------------------- SESSION STATE -------------------------
if "forecast_out" not in st.session_state:
    st.session_state.forecast_out = None

if "tips_out" not in st.session_state:
    st.session_state.tips_out = None

if "year_plots" not in st.session_state:
    st.session_state.year_plots = None

# ------------------------- GREEN ECO CSS -------------------------
st.markdown("""
<style>
:root {
    --green: #2b8a5f;
    --light-green: #e6f5ed;
}
.card {
    background: var(--light-green);
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.07);
}
.metric-title {
    font-size: 13px;
    color: #6c7c74;
}
.metric-value {
    font-size: 22px;
    font-weight: 700;
    color: var(--green);
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADING ------------------
st.markdown("<h2 style='color:#2b8a5f;'>🌿 SmartAI Energy Saver</h2>", unsafe_allow_html=True)

# ------------------ INPUT MODE SWITCH ------------------
mode = st.radio("Choose Input Method:", ["Upload CSV", "Enter Data Manually"])

# ======================================================================
# 🟩 MODE 1 — CSV UPLOAD (Your original system)
# ======================================================================
if mode == "Upload CSV":

    st.write("Upload your electricity bill CSV to analyze usage trends, forecast bills, and get smart insights.")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    st.info("""
    ### Required CSV Format  
    - Bill_ID  
    - Billing_Month  
    - Billing_Year  
    - Units_Consumed_kWh  
    - Total_Amount  
    - Payment_Status  
    """)

    if uploaded_file:
        filepath = os.path.join(DATA_DIR, uploaded_file.name)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = read_csv(filepath)
        st.success("CSV uploaded successfully!")

        # ------------------ KPI CARDS ------------------
        col1, col2, col3 = st.columns(3)

        this_month = int(df["Units_Consumed_kWh"].iloc[-1])
        yearly_total = df[df["Billing_Year"] == df["Billing_Year"].max()]["Units_Consumed_kWh"].sum()
        avg_usage = round(df["Units_Consumed_kWh"].mean(), 1)

        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>This Month Usage</div>
                <div class='metric-value'>{this_month} kWh</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Yearly Total</div>
                <div class='metric-value'>{yearly_total} kWh</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>Average Monthly Usage</div>
                <div class='metric-value'>{avg_usage} kWh</div>
            </div>
            """, unsafe_allow_html=True)

        # ------------------ FORECAST ------------------
        st.markdown("<div class='card'><h3>📈 Forecast</h3>", unsafe_allow_html=True)

        if st.button("Run Forecast"):
            st.session_state.forecast_out = run_forecast(filepath)
            out = st.session_state.forecast_out

            st.write(f"**Predicted Usage:** {out['predicted_usage_kWh']} kWh")
            st.write(f"**Predicted Bill:** ₹{out['predicted_bill_inr']}")
            st.write(f"**MAE:** {out['mae_units']}")
            st.write(f"**R2 Score:** {out['r2_score']}")

            plot_path = os.path.join(FORECAST_DIR, "forecast_plot.png")
            st.image(plot_path, caption="Forecast Plot", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ SMART TIPS ------------------
        st.markdown("<div class='card'><h3>💡 Smart Tips</h3>", unsafe_allow_html=True)

        if st.button("Generate Smart Tips"):
            st.session_state.tips_out = run_tips(filepath)
            out = st.session_state.tips_out

            st.write("### Usage Category:", out["category"])
            for tip in out["tips"]:
                st.write("✔ " + tip)

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ YEARLY ANALYSIS ------------------
        st.markdown("<div class='card'><h3>📆 Yearly Analysis</h3>", unsafe_allow_html=True)

        if st.button("Generate Yearly Comparison Plots"):

            df["Billing_Month"] = df["Billing_Month"].astype(int)
            df["Billing_Year"] = df["Billing_Year"].astype(int)

            p1 = plot_year_comparison(df)
            p2 = plot_year_averages(df)

            st.session_state.year_plots = [p1, p2]

            st.image(p1)
            st.image(p2)

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------ PDF DOWNLOAD ------------------
        st.markdown("<div class='card'><h3>📄 Download PDF Report</h3>", unsafe_allow_html=True)

        if st.button("Download PDF Report"):

            if st.session_state.forecast_out is None:
                st.error("⚠ Please run Forecast first.")
            elif st.session_state.tips_out is None:
                st.error("⚠ Please generate Smart Tips first.")
            elif st.session_state.year_plots is None:
                st.error("⚠ Please run Yearly Analysis first.")
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    pdf_path = tmp_file.name

                generate_pdf_report(
                    pdf_path,
                    st.session_state.forecast_out,
                    st.session_state.tips_out,
                    st.session_state.year_plots
                )

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Electricity Report (PDF)",
                        data=f,
                        file_name="Electricity_Report.pdf",
                        mime="application/pdf"
                    )

        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================
# 🟦 MODE 2 — MANUAL INPUT MODE (Improved UI)
# ======================================================================


# ------------------ INTRO VIDEO ------------------
st.markdown("<h3 style='color:#2b8a5f;'>🎬 Project Introduction Video</h3>", unsafe_allow_html=True)

video_path = "assets/advertisement.mp4"
with open(video_path, "rb") as video_file:
    st.video(video_file.read(), format="video/mp4")
