"""
Hospital Readmission Analysis - Predictive ML Model
Predicts 30-day readmission risk using Random Forest + Logistic Regression.
Outputs feature importance and model metrics.
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, roc_auc_score,
                              roc_curve, confusion_matrix, ConfusionMatrixDisplay)

warnings.filterwarnings("ignore")
os.makedirs("output/charts", exist_ok=True)
os.makedirs("output", exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "#0f1117", "axes.facecolor": "#1a1d27",
    "text.color": "#e0e0e0", "axes.labelcolor": "#b0b3c1",
    "xtick.color": "#b0b3c1", "ytick.color": "#b0b3c1",
    "axes.edgecolor": "#3a3d4d", "grid.color": "#2a2d3d",
})

# ── Load ───────────────────────────────────────────────────────────────────
conn = sqlite3.connect("data/hospital.db")
df = pd.read_sql("SELECT * FROM patients", conn)
conn.close()

# ── Feature engineering ────────────────────────────────────────────────────
le = LabelEncoder()
cat_cols = ["gender","race","insurance_type","primary_diagnosis","discharge_disposition"]
for col in cat_cols:
    df[col + "_enc"] = le.fit_transform(df[col])

feature_cols = [
    "age","num_diagnoses","num_procedures","num_medications",
    "num_lab_tests","num_prior_admissions","length_of_stay","a1c_level",
    "gender_enc","race_enc","insurance_type_enc",
    "primary_diagnosis_enc","discharge_disposition_enc"
]
feature_names = [
    "Age","# Diagnoses","# Procedures","# Medications",
    "# Lab Tests","Prior Admissions","Length of Stay","A1C Level",
    "Gender","Race","Insurance Type","Diagnosis","Discharge Type"
]

X = df[feature_cols].values
y = df["readmitted_30day"].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── Models ─────────────────────────────────────────────────────────────────
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=8,
                                                  random_state=42, n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150,
                                                      learning_rate=0.08,
                                                      max_depth=4, random_state=42),
}

results = {}
for name, model in models.items():
    Xtr = X_train_sc if name == "Logistic Regression" else X_train
    Xte = X_test_sc  if name == "Logistic Regression" else X_test
    model.fit(Xtr, y_train)
    y_pred  = model.predict(Xte)
    y_proba = model.predict_proba(Xte)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    results[name] = {"model": model, "y_pred": y_pred,
                     "y_proba": y_proba, "auc": auc,
                     "X_test": Xte}
    print(f"\n{'─'*50}")
    print(f"  {name}  |  ROC-AUC: {auc:.4f}")
    print(classification_report(y_test, y_pred,
                                 target_names=["Not Readmitted","Readmitted"]))

best_name = max(results, key=lambda k: results[k]["auc"])
best      = results[best_name]
print(f"\n🏆 Best model: {best_name}  (AUC = {best['auc']:.4f})")

# ════════════════════════════════════════════════════════════
# CHART 7 – ROC Curves (all models)
# ════════════════════════════════════════════════════════════
ACCENT, DANGER, SUCCESS, WARN = "#00d4ff", "#ff4b6e", "#00e5a0", "#ffbb44"
colors = [ACCENT, DANGER, SUCCESS]

fig, ax = plt.subplots(figsize=(7, 6))
for (name, res), col in zip(results.items(), colors):
    fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
    ax.plot(fpr, tpr, color=col, linewidth=2,
            label=f"{name} (AUC={res['auc']:.3f})")
ax.plot([0,1],[0,1], "--", color="#555", linewidth=1)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves – Model Comparison", fontsize=14, color="#ffffff", pad=12)
ax.legend(facecolor="#1a1d27", edgecolor="#3a3d4d", fontsize=9)
plt.tight_layout()
plt.savefig("output/charts/07_roc_curves.png", dpi=150)
plt.close()
print("✅ Chart 7 – ROC curves saved")

# ════════════════════════════════════════════════════════════
# CHART 8 – Feature Importance (Random Forest)
# ════════════════════════════════════════════════════════════
rf = results["Random Forest"]["model"]
importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values()

fig, ax = plt.subplots(figsize=(9, 6))
colors_fi = [DANGER if v > importances.median() else ACCENT for v in importances.values]
bars = ax.barh(importances.index, importances.values, color=colors_fi,
               height=0.65, edgecolor="none")
ax.set_title("Feature Importance – Random Forest", fontsize=14,
             color="#ffffff", pad=12)
ax.set_xlabel("Importance Score")
for bar, val in zip(bars, importances.values):
    ax.text(val + 0.001, bar.get_y()+bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=8.5, color="#e0e0e0")
high_patch = mpatches.Patch(color=DANGER, label="Top features")
low_patch  = mpatches.Patch(color=ACCENT, label="Other features")
ax.legend(handles=[high_patch, low_patch],
          facecolor="#1a1d27", edgecolor="#3a3d4d")
plt.tight_layout()
plt.savefig("output/charts/08_feature_importance.png", dpi=150)
plt.close()
print("✅ Chart 8 – Feature importance saved")

# ════════════════════════════════════════════════════════════
# CHART 9 – Confusion Matrix (best model)
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 5))
cm = confusion_matrix(y_test, best["y_pred"])
disp = ConfusionMatrixDisplay(cm, display_labels=["No Readmit", "Readmit"])
disp.plot(ax=ax, colorbar=False, cmap="Blues")
ax.set_title(f"Confusion Matrix – {best_name}", fontsize=13,
             color="#ffffff", pad=10)
plt.tight_layout()
plt.savefig("output/charts/09_confusion_matrix.png", dpi=150)
plt.close()
print("✅ Chart 9 – Confusion matrix saved")

# ── Export risk scores for Power BI ───────────────────────────────────────
rf_model  = results["Random Forest"]["model"]
X_all_sc  = X  # RF doesn't need scaling
risk_scores = rf_model.predict_proba(X_all_sc)[:, 1]
df["readmission_risk_score"] = risk_scores.round(4)
df["risk_tier"] = pd.cut(risk_scores,
                          bins=[0, 0.10, 0.20, 0.35, 1.0],
                          labels=["Low", "Moderate", "High", "Critical"])
df[["patient_id","age","primary_diagnosis","insurance_type",
    "length_of_stay","num_prior_admissions","readmitted_30day",
    "readmission_risk_score","risk_tier"]].to_csv("output/patient_risk_scores.csv",
                                                   index=False)
print("\n✅ Risk scores exported → output/patient_risk_scores.csv")

print("\n📊 Risk Tier Distribution:")
print(df["risk_tier"].value_counts().to_string())
