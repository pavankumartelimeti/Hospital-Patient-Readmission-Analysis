# Power BI Dashboard Setup Guide
## Hospital Readmission Analysis

---

## 📁 Files to Import into Power BI

| File | Use |
|------|-----|
| `data/hospital_patients.csv` | Main patient table |
| `output/patient_risk_scores.csv` | ML risk scores per patient |
| `output/diagnosis_readmission.csv` | Aggregated diagnosis stats |
| `output/insurance_readmission.csv` | Insurance breakdown |
| `output/monthly_trend.csv` | Time-series trend data |

---

## 📊 Recommended Dashboard Pages

### Page 1 — Executive Summary (KPI Cards)
- **Card**: Total Patients (COUNT of patient_id)
- **Card**: Overall Readmission Rate (AVG of readmitted_30day × 100)
- **Card**: Avg Length of Stay (AVG of length_of_stay)
- **Card**: High/Critical Risk Patients (filter risk_tier = High or Critical)

### Page 2 — Readmission Deep Dive
- **Bar Chart**: Readmission Rate by primary_diagnosis
- **Bar Chart**: Readmission Rate by insurance_type
- **Clustered Bar**: Readmission Rate by age group (create DAX bucket)
- **Donut Chart**: Discharge Disposition breakdown

### Page 3 — Trend Analysis
- **Line Chart**: Monthly admissions + readmission rate (from monthly_trend.csv)
- **Area Chart**: Admissions over time by diagnosis (use main table)

### Page 4 — Risk Stratification (ML Insights)
- **Funnel/Bar**: Patient count by risk_tier (Low → Critical)
- **Scatter Plot**: readmission_risk_score vs length_of_stay
- **Table**: Top 20 Critical-risk patients with key metrics
- **Bar Chart**: Risk score distribution by diagnosis

---

## 🔧 DAX Measures to Create

```dax
-- Overall Readmission Rate
Readmission Rate = 
AVERAGE(hospital_patients[readmitted_30day]) * 100

-- Total Readmitted
Total Readmitted = 
SUM(hospital_patients[readmitted_30day])

-- High Risk Count
High Risk Patients = 
CALCULATE(
    COUNTROWS(patient_risk_scores),
    patient_risk_scores[risk_tier] IN {"High", "Critical"}
)

-- Age Group Column (add via Power Query or DAX)
Age Group = 
SWITCH(
    TRUE(),
    hospital_patients[age] < 30, "18-29",
    hospital_patients[age] < 45, "30-44",
    hospital_patients[age] < 60, "45-59",
    hospital_patients[age] < 75, "60-74",
    "75+"
)
```

---

## 🎨 Suggested Color Theme
- Background: `#0f1117` (dark) or white for professional
- Primary accent: `#0078D4` (Power BI blue)
- Alert/High risk: `#E74C3C`
- Success/Low risk: `#27AE60`
- Warning/Moderate: `#F39C12`

---

## 🔗 Table Relationships
Connect tables on `primary_diagnosis` field:
- `hospital_patients` → `diagnosis_readmission` (many-to-one)
- `hospital_patients` → `patient_risk_scores` on `patient_id` (one-to-one)

---

