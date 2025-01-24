#Uarbejdet af Sima & Batoul
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from xml.etree.ElementTree import fromstring
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BASE_URL = "http://80.198.171.108:60030/api"  # Serverens base-URL

# Funktion: Hent patienter fra serveren
def get_patients():
    try:
        response = requests.get(f"{BASE_URL}/get_patients")
        response.raise_for_status()
        xml_data = fromstring(response.text)
        patients = []
        for patient in xml_data.findall('Patient'):
            uid = patient.find('UID').text
            name = patient.find('Name').text  # Fulde navn (fornavn + efternavn)
            patients.append({"uid": uid, "name": name})
        return patients
    except Exception as e:
        messagebox.showerror("Fejl", f"Kunne ikke hente patienter: {e}")
        return []

# Funktion: Hent filtreret data for en patient og gem som XML-fil
def get_filtered_data(uid):
    try:
        response = requests.get(f"{BASE_URL}/filter_patient/{uid}")
        response.raise_for_status()  # Tjek for HTTP-fejl
        return response.text
    except Exception as e:
        messagebox.showerror("Fejl", f"Kunne ikke hente eller gemme data for {uid}: {e}")
        return ""

# Funktion: Ekstraher signal fra XML
def parse_filtered_signal(xml_data):
    try:
        root = fromstring(xml_data)
        signal_data = root.find('FilteredSignal').text
        if not signal_data:
            raise ValueError("Signaldata er tomt eller forkert formatteret.")
        return np.array(list(map(float, signal_data.split(","))))
    except Exception as e:
        messagebox.showerror("Fejl", f"Kunne ikke parse signaldata: {e}")
        return np.array([])

# GUI: Opret hovedvinduet
def create_gui():
    window = tk.Tk()
    window.title("Lægens System")

    # Patientliste med Konsultationer som en del af tabellen
    tk.Label(window, text="Patienter").grid(row=0, column=0, padx=10, pady=5)
    patient_tree = ttk.Treeview(window, columns=("UID", "Navn", "Konsultationer"), show="headings", height=15)
    patient_tree.heading("UID", text="Brugernavn")
    patient_tree.heading("Navn", text="Navn")
    patient_tree.heading("Konsultationer", text="Konsultationer")
    patient_tree.column("UID", width=150, anchor="center")
    patient_tree.column("Navn", width=150, anchor="center")
    patient_tree.column("Konsultationer", width=150, anchor="center")
    patient_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    scrollbar = ttk.Scrollbar(window, orient="vertical", command=patient_tree.yview)
    patient_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=1, sticky="ns")

    # Plotområde
    tk.Label(window, text="Filtrerede Signal Plot").grid(row=0, column=2, padx=10, pady=5)
    plot_frame = tk.Frame(window)
    plot_frame.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")

    # Funktion: Hent og vis patienter
    def load_patients():
        patients = get_patients()
        if patients:
            for patient in patients:
                patient_tree.insert("", "end", values=(patient["uid"], patient["name"], "+"))

    # Funktion: Tilføj konsultation
    def add_consultation(uid, name):
        messagebox.showinfo("Konsultation", f"Tilføjer konsultation for {name} (UID: {uid}).")

    # Funktion: Håndter klik på Konsultationer-kolonnen
    def on_treeview_click(event):
        item = patient_tree.identify_row(event.y)
        column = patient_tree.identify_column(event.x)
        if item and column == "#3":  # "#3" refererer til den tredje kolonne (Konsultationer)
            values = patient_tree.item(item, "values")
            uid = values[0]
            name = values[1]
            add_consultation(uid, name)

    # Funktion: Håndter valg af patient
    def on_patient_select(event):
        selected = patient_tree.selection()
        if selected:
            uid = patient_tree.item(selected[0], "values")[0]
            xml_data = get_filtered_data(uid)
            signal = parse_filtered_signal(xml_data)
            if signal.size > 0:
                plot_signal(signal)
            else:
                messagebox.showwarning("Advarsel", "Ingen gyldig signaldata fundet.")

    # Funktion: Plot signal
    def plot_signal(signal):
        for widget in plot_frame.winfo_children():
            widget.destroy()  # Ryd tidligere plot

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        max_samples = min(5000, len(signal))  # Begræns til 5000 samples for hurtigere rendering
        ax.plot(signal[:max_samples], label="Filtrerede Signal", color="blue")
        ax.set_title("Filtrerede Signal")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    # Hent patienter ved opstart
    load_patients()

    # Bind klik og valg af patient
    patient_tree.bind("<Button-1>", on_treeview_click)  # Håndter klik på kolonner
    patient_tree.bind("<<TreeviewSelect>>", on_patient_select)

    # Tilpas vindue-layout
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
