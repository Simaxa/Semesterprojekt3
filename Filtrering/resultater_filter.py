#udarbejdet Batoul 
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch

# Funktioner til signalbehandling
def remove_baseline_wander(signal, fs):
    cutoff = 0.5  # Afskæringsfrekvens for baseline-drift
    nyquist = 0.5 * fs  # Nyquist-frekvens
    normal_cutoff = cutoff / nyquist
    b, a = butter(1, normal_cutoff, btype='high', analog=False)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def remove_powerline_interference(signal, fs, freq=50):
    quality_factor = 30.0  # Kvalitetsfaktor for notch-filter
    b, a = iirnotch(freq / (fs / 2), quality_factor)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def remove_high_frequency_noise(signal, fs):
    cutoff = 40  # Afskæringsfrekvens for højfrekvent støj
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(4, normal_cutoff, btype='low', analog=False)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

# Læs data
record = wfdb.rdrecord("rec_1")
fs = record.fs  # Samplingfrekvens
signal = record.p_signal[:, 0]  # Første kanal (rå signal)
t = np.arange(0, len(signal)) / fs  # Tidsskala

# Fjern baseline-drift
baseline_removed_signal = remove_baseline_wander(signal, fs)

# Fjern netstøj
powerline_removed_signal = remove_powerline_interference(baseline_removed_signal, fs)

# Fjern højfrekvent støj
clean_signal = remove_high_frequency_noise(powerline_removed_signal, fs)

# --- Plot Baseline-drift ---
plt.figure(figsize=(10, 8))

# Rådata vs. Uden baseline-drift
plt.subplot(2, 1, 1)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, baseline_removed_signal, label="Uden baseline-drift", color='red', linewidth=1)
plt.title("Rådata vs EKG uden baseline-drift", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

# Rådata vs. Med baseline
plt.subplot(2, 1, 2)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, signal, label="Med baseline (ingen ændring)", color='orange', linewidth=1)
plt.title("Rådata vs EKG med baseline", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()

# --- Plot Netstøj ---
plt.figure(figsize=(10, 8))

# Rådata vs. Uden netstøj
plt.subplot(2, 1, 1)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, powerline_removed_signal, label="Uden netstøj", color='green', linewidth=1)
plt.title("Rådata vs EKG uden netstøj", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

# Rådata vs. Med netstøj
plt.subplot(2, 1, 2)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, baseline_removed_signal, label="Med netstøj", color='orange', linewidth=1)
plt.title("Rådata vs EKG med netstøj", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()

# --- Plot Muskelstøj ---
plt.figure(figsize=(10, 8))

# Rådata vs. Uden muskelstøj
plt.subplot(2, 1, 1)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, clean_signal, label="Uden muskelstøj", color='purple', linewidth=1)
plt.title("Rådata vs EKG uden muskelstøj", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

# Rådata vs. Med muskelstøj
plt.subplot(2, 1, 2)
plt.plot(t, signal, label="Rådata", color='blue', linewidth=1)
plt.plot(t, powerline_removed_signal, label="Med muskelstøj", color='orange', linewidth=1)
plt.title("Rådata vs EKG med muskelstøj", fontsize=14)
plt.xlabel("Tid (s)", fontsize=12)
plt.ylabel("Amplitude (mV)", fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()
