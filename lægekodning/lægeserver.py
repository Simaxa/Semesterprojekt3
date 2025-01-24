#Uarbejdet af Sima & Batoul
from flask import Flask, request, Response
import os
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch
import wfdb
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)

BASE_PATH = "/home/sugrp001/site/raw_data"

# Root endpoint for test
@app.route('/', methods=['GET'])
def root():
    return "Serveren kører korrekt!", 200

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test():
    return "Serveren fungerer korrekt!", 200

# Funktion: Fjern baseline-drift
def remove_baseline_wander(signal, fs):
    cutoff = 0.5  # Afskæringsfrekvens for baseline-drift
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(2, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, signal)

# Funktion: Fjern netstøj
def remove_powerline_interference(signal, fs, freq=50):
    quality_factor = 50.0  # Kvalitetsfaktor for notch-filter
    b, a = iirnotch(freq / (fs / 2), quality_factor)
    return filtfilt(b, a, signal)

# Funktion: Fjern højfrekvent støj
def remove_high_frequency_noise(signal, fs):
    cutoff = 40  # Afskæringsfrekvens for højfrekvent støj
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(4, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)

# Endpoint: Hent patienter
@app.route('/api/get_patients', methods=['GET'])
def get_patients():
    try:
        root = Element('Patients')
        for uid in os.listdir(BASE_PATH):
            patient_path = os.path.join(BASE_PATH, uid)
            if os.path.isdir(patient_path):
                patient = SubElement(root, 'Patient')
                SubElement(patient, 'UID').text = uid
                SubElement(patient, 'Name').text = uid.capitalize()
        xml_data = tostring(root, encoding='unicode')
        return Response(xml_data, mimetype='application/xml')
    except Exception as e:
        error = Element('Error')
        error.text = f"Fejl under hentning af patienter: {str(e)}"
        return Response(tostring(error, encoding='unicode'), mimetype='application/xml', status=500)

# Endpoint: Filtrer data og returnér som XML
@app.route('/api/filter_patient/<uid>', methods=['GET'])
def filter_patient(uid):
    try:
        input_file = os.path.join(BASE_PATH, uid, "rec_1")
        dat_file = input_file + ".dat"
        hea_file = input_file + ".hea"

        if not os.path.exists(dat_file) or not os.path.exists(hea_file):
            error = Element('Error')
            error.text = f"Data for patient {uid} findes ikke."
            return Response(tostring(error, encoding='unicode'), mimetype='application/xml', status=404)

        # Læs rådata fra WFDB-fil
        record = wfdb.rdrecord(input_file)
        fs = record.fs  # Samplingfrekvens
        raw_signal = record.p_signal[:, 0]  # Første kanal

        # Filtrér signalet trin-for-trin
        baseline_removed_signal = remove_baseline_wander(raw_signal, fs)
        powerline_removed_signal = remove_powerline_interference(baseline_removed_signal, fs)
        clean_signal = remove_high_frequency_noise(powerline_removed_signal, fs)

        # Opret XML
        root = Element('PatientData')
        SubElement(root, 'UID').text = uid
        filtered_signal = SubElement(root, 'FilteredSignal')
        filtered_signal.text = ','.join(map(str, clean_signal))

        xml_data = tostring(root, encoding='unicode')
        return Response(xml_data, mimetype='application/xml')
    except Exception as e:
        error = Element('Error')
        error.text = f"Fejl under filtrering: {str(e)}"
        return Response(tostring(error, encoding='unicode'), mimetype='application/xml', status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=60030, debug=True)
