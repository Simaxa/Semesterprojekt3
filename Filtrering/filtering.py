#udarbejdet af Khadijah og Batoul 
import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, iirnotch

# Funktioner til signalbehandling
def remove_baseline_wander(signal, fs):
    cutoff = 0.5  # Afskæringsfrekvens for baseline-drift
    nyquist = 0.5 * fs  # Nyquist-frekvens
    normal_cutoff = cutoff / nyquist
    b, a = butter(2, normal_cutoff, btype='high', analog=False)  # 2. ordens filter
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def remove_powerline_interference(signal, fs, freq=50):
    quality_factor = 50.0  # Kvalitetsfaktor for notch-filter
    b, a = iirnotch(freq / (fs / 2), quality_factor)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def remove_high_frequency_noise(signal, fs):
    cutoff = 40  # Afskæringsfrekvens for højfrekvent støj
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(4, normal_cutoff, btype='low', analog=False)  # 4. ordens filter
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

# Plotfunktioner
def plot_time_domain(signal, fs, title, xlabel, ylabel, color, duration=5):
    t = np.arange(0, len(signal)) / fs
    max_samples = int(duration * fs)  # Begræns til ønsket varighed
    t = t[:max_samples]
    signal = signal[:max_samples]
    plt.plot(t, signal, linewidth=1, color=color)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linewidth=0.5, linestyle='--')

def plot_frequency_domain(signal, fs, title, xlabel, ylabel, color):
    freqs = np.fft.rfftfreq(len(signal), 1 / fs)
    fft_magnitude = np.abs(np.fft.rfft(signal))
    plt.plot(freqs, fft_magnitude, linewidth=1, color=color)
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linewidth=0.5, linestyle='--')

# Læs data
record = wfdb.rdrecord("rec_1")
fs = record.fs  # Samplingfrekvens
signal = record.p_signal[:, 0]  # Første kanal (rå signal)

# --- Originalt signal ---
plt.figure(figsize=(8, 12))
plt.subplot(3, 1, 1)
plot_time_domain(signal, fs, "Rå signal med støj", "Tid (s)", "Amplitude (mV)", "black", duration=10)
plt.subplot(3, 1, 2)
plot_frequency_domain(signal, fs, "Rå signal (frekvensdomæne)", "Frekvens (Hz)", "Magnitude (energy)", "black")
plt.tight_layout()
plt.show()

# --- Fjern baseline-drift ---
baseline_removed_signal = remove_baseline_wander(signal, fs)
plt.figure(figsize=(8, 12))
plt.subplot(3, 1, 1)
plot_time_domain(baseline_removed_signal, fs, "EKG uden baseline-drift", "Tid (s)", "Amplitude (mV)", "green", duration=10)
plt.subplot(3, 1, 2)
plot_frequency_domain(baseline_removed_signal, fs, "EKG uden baseline-drift (frekvensdomæne)", "Frekvens (Hz)", "Magnitude (energy)", "green")
plt.tight_layout()
plt.show()

# --- Fjern netstøj ---
powerline_removed_signal = remove_powerline_interference(baseline_removed_signal, fs)
plt.figure(figsize=(8, 12))
plt.subplot(3, 1, 1)
plot_time_domain(powerline_removed_signal, fs, "EKG uden netstøj", "Tid (s)", "Amplitude (mV)", "red", duration=10)
plt.subplot(3, 1, 2)
plot_frequency_domain(powerline_removed_signal, fs, "EKG uden netstøj (frekvensdomæne)", "Frekvens (Hz)", "Magnitude (energy)", "red")
plt.tight_layout()
plt.show()

# --- Fjern muskelstøj ---
clean_signal = remove_high_frequency_noise(powerline_removed_signal, fs)
plt.figure(figsize=(8, 12))
plt.subplot(3, 1, 1)
plot_time_domain(clean_signal, fs, "EKG uden muskelstøj", "Tid (s)", "Amplitude (mV)", "blue", duration=10)
plt.subplot(3, 1, 2)
plot_frequency_domain(clean_signal, fs, "EKG uden muskelstøj (frekvensdomæne)", "Frekvens (Hz)", "Magnitude (energy)", "blue")
plt.tight_layout()
plt.show()
