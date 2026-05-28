# 🏥 Hospital Patient Readmission Analysis
### End-to-End Data Analysis Portfolio Project | Python · SQL · Power BI

---

## 📌 Problem Statement

30-day hospital readmissions cost the U.S. healthcare system over **$26 billion annually**.
This project analyzes 5,000 patient records to:
- Identify the key clinical and social drivers of readmission
- Segment high-risk patients using machine learning
- Deliver actionable insights through an interactive Power BI dashboard

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** (pandas, scikit-learn, matplotlib, seaborn) | Data generation, EDA, ML modeling |
| **SQL** (SQLite) | Data querying, aggregation, profiling |
| **Power BI** | Interactive executive dashboard |

---

## 📁 Project Structure

```
hospital_readmission/
├── data/
│   ├── generate_data.py       # Synthetic dataset generator (5,000 patients)
│   ├── hospital_patients.csv  # Generated CSV
│   └── hospital.db            # SQLite database
├── sql/
│   └── analysis_queries.sql   # 10 analytical SQL queries
├── python/
│   ├── eda.py                 # Exploratory Data Analysis (6 charts)
│   └── ml_model.py            # ML models + feature importance (3 charts)
├── output/
│   ├── charts/                # All 9 generated visualizations
│   ├── patient_risk_scores.csv
│   ├── diagnosis_readmission.csv
│   ├── insurance_readmission.csv
│   └── monthly_trend.csv
├── powerbi/
│   └── dashboard_guide.md     # Power BI setup instructions + DAX measures
└── README.md
```

---

## 🚀 How to Run

### Step 1 – Generate Data
```bash
cd hospital_readmission
python data/generate_data.py
```

### Step 2 – Run EDA
```bash
python python/eda.py
```

### Step 3 – Run ML Model
```bash
python python/ml_model.py
```

### Step 4 – SQL Analysis
```bash
sqlite3 data/hospital.db < sql/analysis_queries.sql
```

### Step 5 – Power BI
Import CSV files from `output/` following `powerbi/dashboard_guide.md`

---

## 📊 Key Findings

| Insight | Value |
|---------|-------|
| Overall 30-day readmission rate | **14.3%** |
| Highest-risk diagnosis | **Heart Failure (~22%)** |
| Highest-risk insurance group | **Uninsured** |
| Avg length of stay | **4.6 days** |
| High/Critical risk patients | **475 (9.5%)** |
| Best ML model (AUC) | **Random Forest (0.61)** |

---

## 💡 Business Recommendations

1. **Discharge planning**: Assign care coordinators to Heart Failure & Sepsis patients
2. **Insurance gap**: Uninsured and Medicaid patients need follow-up call programs
3. **Medication review**: Patients on 10+ medications are significantly higher risk
4. **Prior admissions flag**: Patients with 2+ prior admissions should trigger automatic alerts

---

## 🎯 Skills Demonstrated

- **SQL**: Aggregations, CASE statements, CTEs, window functions, multi-table joins
- **Python**: Data wrangling (pandas), EDA, visualization (matplotlib/seaborn), ML (scikit-learn)
- **Machine Learning**: Logistic Regression, Random Forest, Gradient Boosting, ROC-AUC, cross-validation
- **Power BI**: Data modeling, DAX measures, dashboard design, storytelling
- **Domain Knowledge**: Healthcare analytics, readmission risk factors

---

*Dataset is synthetic and generated for educational/portfolio purposes.*
