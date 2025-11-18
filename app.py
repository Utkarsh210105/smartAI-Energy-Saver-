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
if mode == "Enter Data Manually":

    st.subheader("📝 Enter Monthly Electricity Usage")

    # STEP 1 → Ask user how many months they want to enter
    num_months = st.selectbox(
        "How many months of data do you want to enter?",
        options=list(range(1, 13)),
        index=11  # Default = 12 months
    )

    st.write(f"Please enter electricity units for **{num_months} month(s)**:")

    # Month names for display
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
    units = []

    # STEP 2 → Show exact number of inputs (dynamic)
    for i in range(num_months):
        val = st.number_input(
            f"Units for {month_names[i]}",
            min_value=0,
            max_value=2000,
            value=0,
            key=f"m{i}"
        )
        units.append(val)

    # STEP 3 → Predict button
    if st.button("Predict from Manual Data"):

        valid_units = [u for u in units if u > 0]
        n = len(valid_units)

        if n == 0:
            st.error("Please enter at least 1 non-zero value.")
            st.stop()

        # --- Case 1: Only 1 month ---
        if n == 1:
            predicted_usage = valid_units[-1]
            st.info("Only 1 month given → predicting the same usage for next month.")

        # --- Case 2: 2–5 months ---
        elif n < 6:
            diff = valid_units[-1] - valid_units[-2]
            predicted_usage = valid_units[-1] + diff
            st.info("Small dataset (2–5 months) → using trend-based forecasting.")

        # --- Case 3: 6+ months → Use RandomForest ML Model ---
        else:
            df_manual = pd.DataFrame({
                "Bill_ID": list(range(1, n+1)),
                "Billing_Month": list(range(1, n+1)),
                "Billing_Year": [2024]*n,
                "Units_Consumed_kWh": valid_units,
                "Total_Amount": [u*6 for u in valid_units],
                "Payment_Status": ["Paid"]*n
            })

            temp_path = os.path.join(DATA_DIR, "manual_input.csv")
            df_manual.to_csv(temp_path, index=False)

            out = run_forecast(temp_path)
            predicted_usage = out["predicted_usage_kWh"]

            plot_path = os.path.join(FORECAST_DIR, "forecast_plot.png")
            st.image(plot_path, use_container_width=True)

        # Final Bill Calculation
        predicted_bill = predicted_usage * 6

        st.success(f"Predicted Usage: **{predicted_usage:.2f} kWh**")
        st.success(f"Predicted Bill: **₹{predicted_bill:.2f}**")

# ------------------ INTRO VIDEO ------------------
st.markdown("<h3 style='color:#2b8a5f;'>🎬 Project Introduction Video</h3>", unsafe_allow_html=True)

video_path = "assets/advertisement.mp4"
with open(video_path, "rb") as video_file:
    st.video(video_file.read(), format="video/mp4")
