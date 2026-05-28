"""
Generate synthetic hospital patient data for readmission analysis.
Run this script first to create the dataset.
"""

import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)
N = 5000  # patients

# --- Demographics ---
ages = np.random.normal(60, 15, N).clip(18, 95).astype(int)
genders = np.random.choice(["Male", "Female"], N, p=[0.48, 0.52])
races = np.random.choice(
    ["White", "Black", "Hispanic", "Asian", "Other"],
    N, p=[0.55, 0.20, 0.15, 0.07, 0.03]
)

# --- Clinical ---
diagnoses = np.random.choice(
    ["Heart Failure", "Diabetes", "Pneumonia", "COPD", "Sepsis", "Hip Fracture"],
    N, p=[0.25, 0.22, 0.18, 0.15, 0.12, 0.08]
)
num_diagnoses = np.random.poisson(2.5, N).clip(1, 8)
num_procedures = np.random.poisson(1.8, N).clip(0, 6)
num_medications = np.random.poisson(7, N).clip(1, 20)
length_of_stay = np.random.exponential(5, N).clip(1, 30).astype(int)
num_lab_tests = np.random.poisson(12, N).clip(1, 40)
num_prior_admissions = np.random.poisson(1.2, N).clip(0, 10)

# --- Insurance & Social ---
insurance = np.random.choice(
    ["Medicare", "Medicaid", "Private", "Uninsured"],
    N, p=[0.40, 0.25, 0.28, 0.07]
)
discharge_to = np.random.choice(
    ["Home", "Home with Care", "Skilled Nursing", "Rehab", "AMA"],
    N, p=[0.45, 0.25, 0.18, 0.10, 0.02]
)

# --- Compute readmission probability (realistic logic) ---
readmit_prob = (
    0.05
    + 0.003 * (ages - 50).clip(0)
    + 0.08 * (diagnoses == "Heart Failure")
    + 0.06 * (diagnoses == "Sepsis")
    + 0.05 * (diagnoses == "COPD")
    + 0.04 * (insurance == "Medicaid")
    + 0.03 * (insurance == "Uninsured")
    + 0.04 * (discharge_to == "AMA")
    + 0.015 * num_prior_admissions
    + 0.01 * (num_medications > 10)
    + np.random.normal(0, 0.03, N)
).clip(0.02, 0.75)

readmitted = (np.random.random(N) < readmit_prob).astype(int)

# --- Admission dates (last 3 years) ---
base_date = pd.Timestamp("2022-01-01")
admission_dates = [
    base_date + pd.Timedelta(days=int(np.random.uniform(0, 1095)))
    for _ in range(N)
]
discharge_dates = [
    ad + pd.Timedelta(days=int(los))
    for ad, los in zip(admission_dates, length_of_stay)
]

# --- A1C and glucose for diabetics ---
a1c = np.where(
    diagnoses == "Diabetes",
    np.random.normal(8.2, 1.5, N).clip(5.5, 14),
    np.random.normal(5.6, 0.4, N).clip(4.5, 7)
).round(1)

# --- Build DataFrame ---
df = pd.DataFrame({
    "patient_id": [f"P{str(i).zfill(5)}" for i in range(1, N+1)],
    "age": ages,
    "gender": genders,
    "race": races,
    "insurance_type": insurance,
    "primary_diagnosis": diagnoses,
    "num_diagnoses": num_diagnoses,
    "num_procedures": num_procedures,
    "num_medications": num_medications,
    "num_lab_tests": num_lab_tests,
    "num_prior_admissions": num_prior_admissions,
    "length_of_stay": length_of_stay,
    "a1c_level": a1c,
    "discharge_disposition": discharge_to,
    "admission_date": [d.date() for d in admission_dates],
    "discharge_date": [d.date() for d in discharge_dates],
    "readmitted_30day": readmitted,
})

# --- Save CSV ---
os.makedirs("data", exist_ok=True)
csv_path = "data/hospital_patients.csv"
df.to_csv(csv_path, index=False)
print(f"✅ CSV saved: {csv_path}  ({N} rows)")

# --- Save SQLite DB ---
db_path = "data/hospital.db"
conn = sqlite3.connect(db_path)
df.to_sql("patients", conn, if_exists="replace", index=False)

# Create a second table: department stats
dept_stats = df.groupby("primary_diagnosis").agg(
    total_patients=("patient_id", "count"),
    avg_los=("length_of_stay", "mean"),
    readmission_rate=("readmitted_30day", "mean"),
    avg_medications=("num_medications", "mean"),
).reset_index().rename(columns={"primary_diagnosis": "diagnosis"})
dept_stats["avg_los"] = dept_stats["avg_los"].round(2)
dept_stats["readmission_rate"] = (dept_stats["readmission_rate"] * 100).round(2)
dept_stats["avg_medications"] = dept_stats["avg_medications"].round(2)
dept_stats.to_sql("diagnosis_stats", conn, if_exists="replace", index=False)

conn.close()
print(f"✅ SQLite DB saved: {db_path}")
print(f"\n📊 Dataset preview:")
print(df[["patient_id","age","primary_diagnosis","length_of_stay","readmitted_30day"]].head())
print(f"\n🔢 Readmission rate: {df['readmitted_30day'].mean()*100:.1f}%")
