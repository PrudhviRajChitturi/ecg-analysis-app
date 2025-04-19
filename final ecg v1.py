import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import neurokit2 as nk
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
import csv
import os

# Constants
DATA_FILE = "patient_records.csv"
SAMPLING_RATE = 1000  # Sampling rate in Hz

# Function to get HR limits based on age
def get_hr_limits(age):
    age = int(age)  # Ensure it's an integer
    if age < 1:
        return 100, 180, 100, 180  # Newborn
    elif age < 12:
        return 100, 160, 90, 160  # Infant
    elif age < 36:
        return 90, 150, 80, 150  # Toddler
    elif age < 72:
        return 80, 140, 70, 140  # Preschool
    elif age < 144:
        return 70, 120, 60, 120  # School-age
    elif age < 216:
        return 60, 100, 50, 100  # Teen
    elif age < 780:
        return 60, 100, 50, 100  # Adult
    else:
        return 50, 100, 50, 100  # Senior

# Function to generate suggestions based on analysis results
def generate_suggestions(avg_hr, brady_percent, tachy_percent, arrhythmia_percent, age):
    suggestions = []

    if brady_percent > 5 and brady_percent < 15:
        suggestions.append("Mild Bradycardia detected. If you have any other symptoms consult doctor or take it easy.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion
    elif brady_percent > 15:
        suggestions.append("Bradycardia detected. Please consult a healthcare provider.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion

    # Check for tachycardia
    if tachy_percent > 5 and tachy_percent < 15:
        suggestions.append("Mild Tachycardia detected. If you have any other symptoms consult doctor or take it easy.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion
    elif tachy_percent > 15:
        suggestions.append("Tachycardia detected. Please consult a healthcare provider.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion

    # Check for arrhythmias
    if arrhythmia_percent > 5 and arrhythmia_percent < 15:
        suggestions.append("Mild arrhythmia detected. If you have any other symptoms consult doctor or take it easy.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion
    elif arrhythmia_percent > 15:
        suggestions.append("Arrhythmia detected. Please consult a healthcare provider.")
        return "\n".join(suggestions)  # Stop further checks and return suggestion

    # Check average heart rate against limits
    lower_limit, upper_limit, brady_limit, tachy_limit = get_hr_limits(age)
    if avg_hr < lower_limit:
        suggestions.append(
            f"Your average heart rate is below normal ({avg_hr:.2f} bpm). Please consult a healthcare provider.")
    elif avg_hr > upper_limit:
        suggestions.append(
            f"Your average heart rate is above normal ({avg_hr:.2f} bpm). Please consult a healthcare provider.")

    # Age-specific suggestions
    if age < 18:
        suggestions.append("Ensure regular check-ups with a pediatrician.")
    elif age >= 60:
        suggestions.append("Regular cardiovascular check-ups are recommended.")

    # If any suggestions were made, return all suggestions
    if suggestions:
        return "\n".join(suggestions)  # Return all suggestions
    else:
        return "Your health appears to be fine. Continue regular check-ups."

# Function to perform ECG analysis
def analyze_ecg():
    try:
        # Load ECG signal
        file_path = file_path_entry.get()
        mat_data = loadmat(file_path)
        ecg_signal = mat_data["val"].flatten()

        # Get age-based HR limits
        age = age_entry.get()
        if not age.isdigit():
            messagebox.showerror("Error", "Please enter a valid age.")
            return

        normal_min, normal_max, brady_limit, tachy_limit = get_hr_limits(int(age))

        # Process ECG signal
        ecg_processed, ecg_info = nk.ecg_process(ecg_signal, sampling_rate=SAMPLING_RATE)

        # Extract R-peaks
        r_peaks = ecg_info["ECG_R_Peaks"]

        # Calculate RR intervals and heart rate
        rr_intervals = np.diff(r_peaks) / SAMPLING_RATE
        heart_rate = 60 / rr_intervals

        # Calculate average heart rate
        average_hr = np.mean(heart_rate)

        # Detect bradycardia and tachycardia based on age-adjusted limits
        bradycardia = heart_rate < brady_limit
        tachycardia = heart_rate > tachy_limit
        brady_percent = np.sum(bradycardia) / len(heart_rate) * 100
        tachy_percent = np.sum(tachycardia) / len(heart_rate) * 100

        # Detect arrhythmias using HR variability
        rr_mean = np.mean(rr_intervals)
        rr_sd = np.std(rr_intervals)
        arrhythmias = (rr_intervals < (rr_mean - 2 * rr_sd)) | (rr_intervals > (rr_mean + 2 * rr_sd))
        arrhythmia_percent = np.sum(arrhythmias) / len(rr_intervals) * 100

        # Format results
        results = (
            f"Age: {age} years\n"
            f"Normal HR Range: {normal_min}-{normal_max} bpm\n"
            f"Average HR: {average_hr:.2f} bpm\n"
            f"Bradycardia detected in {brady_percent:.2f}% of beats (Threshold: < {brady_limit} bpm).\n"
            f"Tachycardia detected in {tachy_percent:.2f}% of beats (Threshold: > {tachy_limit} bpm).\n"
            f"Arrhythmias detected in {arrhythmia_percent:.2f}% of beats.\n"
        )
        if arrhythmia_percent > 50:
            results += "⚠️ Extreme Case: Severe arrhythmia detected."

        # Show results in the UI
        result_text.configure(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, results)
        result_text.configure(state="disabled")

        # Generate suggestions based on the analysis
        suggestions = generate_suggestions(average_hr, brady_percent, tachy_percent, arrhythmia_percent, int(age))
        result_text.configure(state="normal")
        result_text.insert(tk.END, "\n--- Suggestions ---\n" + suggestions)
        result_text.configure(state="disabled")

        # Compare with previous records
        compare_with_previous_records(average_hr, brady_percent, tachy_percent, arrhythmia_percent)

        # Save results to file
        save_patient_data(average_hr, brady_percent, tachy_percent, arrhythmia_percent)

        plt.figure(figsize=(14, 6))
        plt.plot(ecg_processed["ECG_Clean"], label="Cleaned ECG Signal", color="blue")
        plt.scatter(r_peaks, ecg_processed["ECG_Clean"][r_peaks], color="red", label="R-peaks")
        plt.title(f"ECG Signal with Abnormalities (Avg HR: {average_hr:.2f} bpm)")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to save patient data to a CSV file
def save_patient_data(avg_hr, brady_percent, tachy_percent, arrhythmia_percent):
    patient_data = {
        "Name": name_entry.get(),
        "Age": age_entry.get(),
        "Gender": gender_var.get(),
        "Height": height_entry.get(),
        "Weight": weight_entry.get(),
        "Sleep Time": sleep_time_entry.get(),
        "Steps": steps_entry.get(),
        "Avg HR": f"{avg_hr:.2f}",
        "Bradycardia %": f"{brady_percent:.2f}",
        "Tachycardia %": f"{tachy_percent:.2f}",
        "Arrhythmia %": f"{arrhythmia_percent:.2f}",
    }

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=patient_data.keys())
        if not file_exists:
            writer.writeheader()  # Write header only once
        writer.writerow(patient_data)

    messagebox.showinfo("Success", "Patient data and ECG analysis saved successfully!")

# Function to compare with previous records
def compare_with_previous_records(avg_hr, brady_percent, tachy_percent, arrhythmia_percent):
    name = name_entry.get()
    previous_data = []

    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Name"] == name:
                    previous_data.append(row)

    if previous_data:
        last_record = previous_data[-1]  # Get the most recent record
        comparison_results = (
            f"\n\n--- Previous Record Comparison ---\n"
            f"Avg HR: {last_record['Avg HR']} bpm (New: {avg_hr:.2f} bpm)\n"
            f"Bradycardia %: {last_record['Bradycardia %']} (New: {brady_percent:.2f})\n"
            f"Tachycardia %: {last_record['Tachycardia %']} (New: {tachy_percent:.2f})\n"
            f"Arrhythmia %: {last_record['Arrhythmia %']} (New: {arrhythmia_percent:.2f})\n"
        )
        result_text.configure(state="normal")
        result_text.insert(tk.END, comparison_results)
        result_text.configure(state="disabled")

    else:
        messagebox.showinfo("No Previous Records", "No previous records found for this patient.")

# Function to view previous records
def view_records():
    if not os.path.isfile(DATA_FILE):
        messagebox.showwarning("No Records", "No records found!")
        return

    record_window = tk.Toplevel(root)
    record_window.title("Patient Records")
    record_window.geometry("800x400")  # Smaller default size for the table window

    # Create a frame for table and scrollbars
    table_frame = ttk.Frame(record_window)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create scrollbars
    y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Create the Treeview table
    tree = ttk.Treeview(
        table_frame,
        columns=(
            "Name", "Age", "Gender", "Height", "Weight", "Sleep Time", "Steps",
            "Avg HR", "Bradycardia %", "Tachycardia %", "Arrhythmia %"
        ),
        show="headings",
        yscrollcommand=y_scrollbar.set,
        xscrollcommand=x_scrollbar.set,
    )
    tree.pack(fill=tk.BOTH, expand=True)

    # Configure scrollbars
    y_scrollbar.config(command=tree.yview)
    x_scrollbar.config(command=tree.xview)

    # Define column headers and set smaller widths
    columns = [
        ("Name", 100), ("Age", 50), ("Gender", 80), ("Height", 80), ("Weight", 80),
        ("Sleep Time", 100), ("Steps", 100), ("Avg HR", 80),
        ("Bradycardia %", 100), ("Tachycardia %", 100), ("Arrhythmia %", 100),
    ]
    for col_name, col_width in columns:
        tree.heading(col_name, text=col_name)
        tree.column(col_name, width=col_width, anchor="center")

    # Load data into the table
    with open(DATA_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            tree.insert("", tk.END, values=list(row.values()))

# Function to select file
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("MAT Files", "*.mat")])
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

# Function to clear the form
def clear_form():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    gender_var.set("Male")
    height_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    sleep_time_entry.delete(0, tk.END)
    steps_entry.delete(0, tk.END)
    file_path_entry.delete(0, tk.END)
    result_text.configure(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.configure(state="disabled")

# Create the UI
root = tk.Tk()
root.title("ECG Analysis Tool")
root.geometry("700x700")

style = ttk.Style(root)
style.theme_use("clam")

# Patient details inputs
patient_frame = ttk.LabelFrame(root, text="Patient Details")
patient_frame.pack(pady=10, fill="x", padx=10)

ttk.Label(patient_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
name_entry = ttk.Entry(patient_frame)
name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Age:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
age_entry = ttk.Entry(patient_frame)
age_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Gender:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
gender_var = tk.StringVar(value="Male")
ttk.OptionMenu(patient_frame, gender_var, "Male", "Female", "Other").grid(row=1, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Height (cm):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
height_entry = ttk.Entry(patient_frame)
height_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Weight (kg):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
weight_entry = ttk.Entry(patient_frame)
weight_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Sleep Time (hours):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
sleep_time_entry = ttk.Entry(patient_frame)
sleep_time_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

ttk.Label(patient_frame, text="Number of Steps:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
steps_entry = ttk.Entry(patient_frame)
steps_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# ECG file input
ecg_frame = ttk.LabelFrame(root, text="ECG Analysis")
ecg_frame.pack(pady=10, fill="x", padx=10)

ttk.Label(ecg_frame, text="ECG File Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
file_path_entry = ttk.Entry(ecg_frame, width=50)
file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(ecg_frame, text="Browse", command=select_file).grid(row=0, column=2, padx=5, pady=5)

# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Analyze", command=analyze_ecg).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="View Records", command=view_records).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Clear", command=clear_form).pack(side=tk.LEFT, padx=5)

# Results display
result_frame = ttk.LabelFrame(root, text="Results")
result_frame.pack(pady=10, fill="both", expand=True, padx=10)
result_text = tk.Text(result_frame, height=10, state="disabled", wrap="word", bg="lightyellow")
result_text.pack(fill="both", expand=True, padx=10, pady=10)

# Configure grid weights for resizing
for i in range(4):
    patient_frame.grid_columnconfigure(i, weight=1)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)

root.mainloop()