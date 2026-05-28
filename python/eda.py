"""
Hospital Readmission Analysis - Exploratory Data Analysis
Generates charts saved to output/charts/ for Power BI import or standalone use.
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("output/charts", exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#3a3d4d",
    "text.color":       "#e0e0e0",
    "axes.labelcolor":  "#b0b3c1",
    "xtick.color":      "#b0b3c1",
    "ytick.color":      "#b0b3c1",
    "grid.color":       "#2a2d3d",
    "font.family":      "DejaVu Sans",
})
ACCENT   = "#00d4ff"
DANGER   = "#ff4b6e"
SUCCESS  = "#00e5a0"
WARN     = "#ffbb44"
PALETTE  = [ACCENT, DANGER, SUCCESS, WARN, "#b088f9", "#ff8c69"]

# ── Load data ──────────────────────────────────────────────────────────────
conn = sqlite3.connect("data/hospital.db")
df   = pd.read_sql("SELECT * FROM patients", conn)
conn.close()

df["admission_date"] = pd.to_datetime(df["admission_date"])
df["discharge_date"] = pd.to_datetime(df["discharge_date"])
df["age_group"] = pd.cut(df["age"], bins=[17,29,44,59,74,100],
                          labels=["18-29","30-44","45-59","60-74","75+"])

print(f"Dataset: {len(df):,} patients  |  Readmission rate: {df['readmitted_30day'].mean()*100:.1f}%\n")

# ════════════════════════════════════════════════════════════
# CHART 1 – Readmission Rate by Diagnosis
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))
diag = (df.groupby("primary_diagnosis")["readmitted_30day"]
          .mean()
          .sort_values(ascending=True) * 100)
colors = [DANGER if v > 18 else ACCENT for v in diag.values]
bars = ax.barh(diag.index, diag.values, color=colors, height=0.6, edgecolor="none")
for bar, val in zip(bars, diag.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=10, color="#e0e0e0")
ax.set_xlabel("Readmission Rate (%)")
ax.set_title("30-Day Readmission Rate by Primary Diagnosis", fontsize=14,
             color="#ffffff", pad=14)
ax.axvline(df["readmitted_30day"].mean()*100, color=WARN, linestyle="--",
           linewidth=1.2, label=f"Overall avg: {df['readmitted_30day'].mean()*100:.1f}%")
ax.legend(facecolor="#1a1d27", edgecolor="#3a3d4d")
ax.set_xlim(0, diag.max() * 1.2)
plt.tight_layout()
plt.savefig("output/charts/01_readmission_by_diagnosis.png", dpi=150)
plt.close()
print("✅ Chart 1 saved")

# ════════════════════════════════════════════════════════════
# CHART 2 – Age Group Analysis (dual bar)
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
age_stats = df.groupby("age_group", observed=True).agg(
    readmission_rate=("readmitted_30day", "mean"),
    avg_los=("length_of_stay", "mean")
).reset_index()

axes[0].bar(age_stats["age_group"], age_stats["readmission_rate"]*100,
            color=PALETTE[:5], edgecolor="none", width=0.6)
axes[0].set_title("Readmission Rate by Age Group", color="#ffffff", fontsize=12)
axes[0].set_ylabel("Readmission Rate (%)")
for i, v in enumerate(age_stats["readmission_rate"]*100):
    axes[0].text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)

axes[1].bar(age_stats["age_group"], age_stats["avg_los"],
            color=PALETTE[:5], edgecolor="none", width=0.6)
axes[1].set_title("Avg Length of Stay by Age Group", color="#ffffff", fontsize=12)
axes[1].set_ylabel("Days")
for i, v in enumerate(age_stats["avg_los"]):
    axes[1].text(i, v + 0.05, f"{v:.1f}", ha="center", fontsize=9)

fig.suptitle("Patient Age Group Analysis", fontsize=15, color="#ffffff", y=1.02)
plt.tight_layout()
plt.savefig("output/charts/02_age_group_analysis.png", dpi=150)
plt.close()
print("✅ Chart 2 saved")

# ════════════════════════════════════════════════════════════
# CHART 3 – Insurance Type Impact
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 5))
ins = (df.groupby("insurance_type")["readmitted_30day"]
         .mean()
         .sort_values(ascending=False) * 100)
bars = ax.bar(ins.index, ins.values, color=PALETTE[:4], edgecolor="none", width=0.5)
ax.set_title("Readmission Rate by Insurance Type", fontsize=14, color="#ffffff", pad=14)
ax.set_ylabel("Readmission Rate (%)")
ax.axhline(df["readmitted_30day"].mean()*100, color=WARN, linestyle="--",
           linewidth=1.2, label="Overall avg")
for bar, val in zip(bars, ins.values):
    ax.text(bar.get_x()+bar.get_width()/2, val+0.2, f"{val:.1f}%",
            ha="center", fontsize=11, color="#ffffff", fontweight="bold")
ax.legend(facecolor="#1a1d27", edgecolor="#3a3d4d")
plt.tight_layout()
plt.savefig("output/charts/03_insurance_impact.png", dpi=150)
plt.close()
print("✅ Chart 3 saved")

# ════════════════════════════════════════════════════════════
# CHART 4 – Correlation Heatmap
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 7))
numeric_cols = ["age","num_diagnoses","num_procedures","num_medications",
                "num_lab_tests","num_prior_admissions","length_of_stay",
                "a1c_level","readmitted_30day"]
corr = df[numeric_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
cmap = sns.diverging_palette(220, 20, as_cmap=True)
sns.heatmap(corr, mask=mask, cmap=cmap, center=0,
            annot=True, fmt=".2f", annot_kws={"size": 9},
            linewidths=0.5, linecolor="#0f1117",
            ax=ax, cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation Matrix", fontsize=14, color="#ffffff", pad=14)
ax.tick_params(colors="#b0b3c1")
plt.tight_layout()
plt.savefig("output/charts/04_correlation_heatmap.png", dpi=150)
plt.close()
print("✅ Chart 4 saved")

# ════════════════════════════════════════════════════════════
# CHART 5 – Monthly Trend
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 5))
monthly = (df.groupby(df["admission_date"].dt.to_period("M"))
             .agg(admissions=("patient_id","count"),
                  readmissions=("readmitted_30day","sum"))
             .reset_index())
monthly["month"] = monthly["admission_date"].astype(str)
monthly["readmission_rate"] = monthly["readmissions"] / monthly["admissions"] * 100

ax2 = ax.twinx()
ax.bar(monthly["month"], monthly["admissions"], color=ACCENT, alpha=0.35,
       label="Admissions", zorder=1)
ax2.plot(monthly["month"], monthly["readmission_rate"], color=DANGER,
         linewidth=2.2, marker="o", markersize=4, label="Readmission %", zorder=2)
ax.set_title("Monthly Admissions & Readmission Rate Trend (2022-2024)",
             fontsize=14, color="#ffffff", pad=14)
ax.set_ylabel("Admissions", color=ACCENT)
ax2.set_ylabel("Readmission Rate (%)", color=DANGER)
ax.tick_params(axis="x", rotation=45, labelsize=7)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, facecolor="#1a1d27", edgecolor="#3a3d4d")
plt.tight_layout()
plt.savefig("output/charts/05_monthly_trend.png", dpi=150)
plt.close()
print("✅ Chart 5 saved")

# ════════════════════════════════════════════════════════════
# CHART 6 – Discharge Disposition
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
disc = (df.groupby("discharge_disposition")["readmitted_30day"]
          .mean()
          .sort_values(ascending=False) * 100)
colors = [DANGER if v > 20 else ACCENT for v in disc.values]
bars = ax.bar(disc.index, disc.values, color=colors, edgecolor="none", width=0.55)
ax.set_title("Readmission Rate by Discharge Disposition", fontsize=14,
             color="#ffffff", pad=14)
ax.set_ylabel("Readmission Rate (%)")
ax.axhline(df["readmitted_30day"].mean()*100, color=WARN, linestyle="--",
           linewidth=1.2, label="Overall avg")
for bar, val in zip(bars, disc.values):
    ax.text(bar.get_x()+bar.get_width()/2, val+0.2, f"{val:.1f}%",
            ha="center", fontsize=10, color="#ffffff")
ax.legend(facecolor="#1a1d27", edgecolor="#3a3d4d")
plt.tight_layout()
plt.savefig("output/charts/06_discharge_disposition.png", dpi=150)
plt.close()
print("✅ Chart 6 saved")

# ── Summary stats export for Power BI ─────────────────────────────────────
summary = {
    "diagnosis_readmission": (df.groupby("primary_diagnosis")
        .agg(patients=("patient_id","count"),
             readmission_rate=("readmitted_30day","mean"),
             avg_los=("length_of_stay","mean"),
             avg_medications=("num_medications","mean"))
        .reset_index()),
    "insurance_readmission": (df.groupby("insurance_type")
        .agg(patients=("patient_id","count"),
             readmission_rate=("readmitted_30day","mean"))
        .reset_index()),
    "monthly_trend": monthly[["month","admissions","readmissions","readmission_rate"]],
}
for name, tbl in summary.items():
    tbl["readmission_rate"] = (tbl["readmission_rate"] * 100).round(2) \
        if "readmission_rate" in tbl.columns and tbl["readmission_rate"].max() <= 1 \
        else tbl.get("readmission_rate", pd.Series()).round(2)
    tbl.to_csv(f"output/{name}.csv", index=False)

print("\n✅ All charts + CSVs exported to output/")
print("\n📊 KEY FINDINGS:")
top_diag = df.groupby("primary_diagnosis")["readmitted_30day"].mean().idxmax()
print(f"  • Highest-risk diagnosis:  {top_diag}")
top_ins  = df.groupby("insurance_type")["readmitted_30day"].mean().idxmax()
print(f"  • Highest-risk insurance:  {top_ins}")
print(f"  • Overall readmission rate: {df['readmitted_30day'].mean()*100:.1f}%")
print(f"  • Avg length of stay: {df['length_of_stay'].mean():.1f} days")
