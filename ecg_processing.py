import wfdb
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
from sklearn.linear_model import LogisticRegression

# Dummy ML model (trained on synthetic patterns)
model = LogisticRegression()

# Synthetic training data
X_train = np.array([
    [0.08, 0.5],  # stable
    [0.05, 1.0],  # moderate
    [0.02, 2.0],  # high risk
])
y_train = np.array([0, 1, 2])

model.fit(X_train, y_train)

def bandpower(signal, fs, low, high):
    nyq = 0.5 * fs
    low /= nyq
    high /= nyq
    b, a = butter(4, [low, high], btype='band')
    filtered = filtfilt(b, a, signal)
    return np.mean(filtered ** 2)

def analyze_ecg(record_name):

    record = wfdb.rdrecord(record_name)
    signal = record.p_signal[:, 0]
    fs = record.fs

    signal = (signal - np.mean(signal)) / np.std(signal)

    peaks, _ = find_peaks(signal, distance=fs*0.6, height=0.8)

    rr_intervals = np.diff(peaks) / fs
    heart_rate = 60 / rr_intervals
    avg_hr = np.mean(heart_rate)

    sdnn = np.std(rr_intervals)
    rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))

    # EEG Simulation
    eeg_fs = 256
    t = np.linspace(0, 10, eeg_fs * 10)
    eeg_signal = (
        0.6*np.sin(2*np.pi*10*t) +
        0.3*np.sin(2*np.pi*20*t) +
        0.2*np.random.randn(len(t))
    )

    alpha_power = bandpower(eeg_signal, eeg_fs, 8, 12)
    beta_power = bandpower(eeg_signal, eeg_fs, 13, 30)
    stress_index = beta_power / alpha_power
    coupling_index = stress_index * (1/(rmssd+0.001))

    # ML Prediction
    prediction = model.predict([[rmssd, stress_index]])[0]

    if prediction == 0:
        status = "🟢 Stable"
    elif prediction == 1:
        status = "🟡 Moderate Risk"
    else:
        status = "🔴 High Risk"

    risk_score = min(100, max(0, coupling_index*20))

    return {
        "Average_HR": round(avg_hr,2),
        "SDNN": round(sdnn,4),
        "RMSSD": round(rmssd,4),
        "Alpha_Power": round(alpha_power,4),
        "Beta_Power": round(beta_power,4),
        "Stress_Index": round(stress_index,4),
        "Coupling_Index": round(coupling_index,4),
        "Risk_Score": round(risk_score,2),
        "Status": status,
        "Signal": signal,
        "Peaks": peaks
    }