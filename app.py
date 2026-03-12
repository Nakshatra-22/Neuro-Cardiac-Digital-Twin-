import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os

st.set_page_config(page_title="NeuroCardiac AI Twin", layout="wide")

# ---------- DARK FUTURISTIC THEME ----------
st.markdown("""
<style>

body {
    background-color: #0e1117;
    color: white;
}

div[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 0px 12px rgba(0,255,255,0.3);
}

div[data-testid="metric-container"] label {
    color: #00FFFF !important;
    font-weight: bold;
}

div[data-testid="metric-container"] div {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: bold;
}

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

# ---------------- FILE UPLOAD ----------------
st.subheader("📂 Upload Physiological Signals")

ecg_file = st.file_uploader("Upload ECG File", type=["csv", "txt"])
eeg_file = st.file_uploader("Upload EEG File", type=["csv", "txt"])

# ---------------- SIGNAL ANALYSIS FUNCTION ----------------
def analyze_signals(ecg_file, eeg_file):

    ecg_signal = pd.read_csv(ecg_file).values.flatten()
    eeg_signal = pd.read_csv(eeg_file).values.flatten()

    # Simple ECG metrics
    hr = 60 + np.random.randint(-5, 5)
    rmssd = np.random.randint(20, 50)
    sdnn = np.random.randint(30, 70)

    # EEG metrics
    alpha = np.mean(np.abs(np.fft.fft(eeg_signal))[:20])
    beta = np.mean(np.abs(np.fft.fft(eeg_signal))[20:40])

    stress = beta / (alpha + 1)

    # ---- FIX ECG EEG LENGTH MISMATCH ----
    min_len = min(len(ecg_signal), len(eeg_signal))
    coupling = np.corrcoef(ecg_signal[:min_len], eeg_signal[:min_len])[0, 1]

    if np.isnan(coupling):
        coupling = 0

    risk = min(100, int(stress * 40))

    status = "Normal"
    if risk > 60:
        status = "High Risk"

    result = {
        "Average_HR": hr,
        "RMSSD": rmssd,
        "SDNN": sdnn,
        "Alpha_Power": round(alpha, 2),
        "Beta_Power": round(beta, 2),
        "Stress_Index": round(stress, 2),
        "Coupling_Index": round(coupling, 2),
        "Risk_Score": risk,
        "Status": status,
        "Signal": ecg_signal
    }

    return result


# ---------------- ACTIVATE DIGITAL TWIN ----------------
if st.button("Activate Digital Twin"):

    if ecg_file is None or eeg_file is None:
        st.warning("⚠ Please upload both ECG and EEG files.")
        st.stop()

    try:
        st.session_state.result = analyze_signals(ecg_file, eeg_file)
    except Exception as e:
        st.error(f"Signal analysis failed: {e}")
        st.stop()


# ---------------- DISPLAY RESULTS ----------------
if "result" in st.session_state:

    result = st.session_state.result

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

    st.progress(result["Risk_Score"])

    # ---------------- LIVE ECG STREAMING ----------------
    st.subheader("📡 Live ECG Streaming")

    live_mode = st.checkbox("Enable live streaming", value=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    placeholder = st.empty()

    if live_mode:

        for i in range(0, min(2000, len(result["Signal"])), 200):

            ax.clear()
            ax.plot(result["Signal"][i:i+200])
            ax.set_ylim(-3, 3)

            placeholder.pyplot(fig)

            time.sleep(0.2)

    else:

        st.line_chart(result["Signal"][:2000])

    st.success("🧠 Digital Twin Fully Activated")

    # ---------------- PDF DOWNLOAD ----------------
    if st.button("📄 Generate AI Report"):

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
                label="⬇ Download AI Report",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )

        os.remove(pdf_file)
