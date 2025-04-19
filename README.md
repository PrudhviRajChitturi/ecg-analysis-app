# 🫀 ECG Analysis Tool

A desktop-based biomedical signal processing application that analyzes ECG data, detects heart abnormalities, and compares patient records over time using Python. Built with a GUI using Tkinter and powered by NeuroKit2, NumPy, Matplotlib, and SciPy.

---

## 🚀 Features

- 📁 Load `.mat` format ECG files.
- 🧠 Detect **bradycardia**, **tachycardia**, and **arrhythmia** using heart rate variability (HRV) and signal processing.
- 📊 Visualize cleaned ECG signals and R-peaks.
- 📂 Maintain and view historical **patient records** with metrics and vital signs.
- 🔁 Compare **new ECG results** with previous data to detect improvements or deterioration.
- 💡 Auto-generate medical **suggestions** based on age-specific heart rate thresholds.

---

## 🛠 Technologies Used

- 🐍 Python 3.x
- 🧪 [NeuroKit2](https://neurokit2.readthedocs.io/)
- 📈 Matplotlib
- 🧮 NumPy, SciPy
- 🪟 Tkinter (GUI)
- 📋 CSV for storing patient records

---

## ⚙️ How to Run

1. **Clone the Repository**:
   bash
   
   git clone https://github.com/PrudhviRajChitturi/ecg-analysis-app.git
   cd ecg-analysis-app

2. **Install Dependencies**:
	bash
	
	pip install -r requirements.txt

3. **Launch the App**:
	bash
	
	python final-ecg-v1.py

##  📚 Record Tracking

The tool creates/updates a patient_records.csv file to store:
	1.Name, Age, Gender, Height, Weight
	2.Sleep Time, Step Count
	3.Average HR, Bradycardia %, Tachycardia %, Arrhythmia %
	
## 🧑‍💻 Author

Chitturi Prudhvi Raj
	-GitHub-	https://github.com/PrudhviRajChitturi
	-LinkedIn-	https://www.linkedin.com/in/prudhvi-raj-chitturi
	-📧Email-	rprudhvi144@gmail.com
	
##⚖️ License
This project is open-source and available under the MIT License.
