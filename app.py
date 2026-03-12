import streamlit as st
import glob
import matplotlib.pyplot as plt
import time
from ecg_processing import analyze_ecg
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os

st.set_page_config(page_title="NeuroCardiac AI Twin", layout="wide")

# ---------- DARK FUTURISTIC THEME WITH CLEAR METRICS ----------
st.markdown("""
<style>

/* Background */
body {
    background-color: #0e1117;
    color: white;
}

/* Metric Box */
div[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 0px 12px rgba(0,255,255,0.3);
}

/* Metric Label */
div[data-testid="metric-container"] label {
    color: #00FFFF !important;
    font-weight: bold;
}

/* Metric Value */
div[data-testid="metric-container"] div {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: bold;
}

/* Buttons */
.stButton>button {
    background-color: #00FFFF;
    color: black;
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------------

st.title("🧠❤️ NeuroCardiac AI Digital Twin")
st.markdown("### Real-Time Brain–Heart Intelligence System")

available=sorted({f.split(".")[0]for f in glob.glob(".hea")})
record_name=st.selectbox("Select ECG Record",available)

if st.button("Activate Digital Twin"):

    result = analyze_ecg(record_name)

    # ---------------- CARDIAC METRICS ----------------
    st.subheader("🩺 Cardiac Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Heart Rate (BPM)", result["Average_HR"])
    col2.metric("RMSSD", result["RMSSD"])
    col3.metric("SDNN", result["SDNN"])

    # ---------------- EEG METRICS ----------------
    st.subheader("🧠 EEG Metrics")
    col4, col5, col6 = st.columns(3)
    col4.metric("Alpha Power", result["Alpha_Power"])
    col5.metric("Beta Power", result["Beta_Power"])
    col6.metric("Stress Index", result["Stress_Index"])

    # ---------------- AI RISK ----------------
    st.subheader("🔗 AI Risk Intelligence")
    col7, col8 = st.columns(2)
    col7.metric("Coupling Index", result["Coupling_Index"])
    col8.metric("ML Status", result["Status"])

    st.progress(int(result["Risk_Score"]))

    # ---------------- LIVE ECG STREAMING ----------------
    st.subheader("📡 Live ECG Streaming")

    fig, ax = plt.subplots(figsize=(10, 4))
    placeholder = st.empty()

    for i in range(0, 2000, 200):
        ax.clear()
        ax.plot(result["Signal"][i:i+200])
        ax.set_ylim(-3, 3)
        placeholder.pyplot(fig)
        time.sleep(0.2)

    st.success("🧠 Digital Twin Fully Activated")

    # ---------------- PDF DOWNLOAD ----------------
    if st.button("📄 Download AI Report as PDF"):

        pdf_file = "NeuroCardiac_Report.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("<b>NeuroCardiac Digital Twin Report</b>", styles["Title"]))
        elements.append(Spacer(1, 0.3 * inch))

        data = [
            ["Metric", "Value"],
            ["Average HR", str(result["Average_HR"])],
            ["RMSSD", str(result["RMSSD"])],
            ["SDNN", str(result["SDNN"])],
            ["Alpha Power", str(result["Alpha_Power"])],
            ["Beta Power", str(result["Beta_Power"])],
            ["Stress Index", str(result["Stress_Index"])],
            ["Coupling Index", str(result["Coupling_Index"])],
            ["Risk Score", str(result["Risk_Score"])],
            ["Status", result["Status"]],
        ]

        table = Table(data)
        elements.append(table)

        doc.build(elements)

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="⬇ Click Here to Download",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )

        os.remove(pdf_file)
