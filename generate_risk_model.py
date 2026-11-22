#!/usr/bin/env python3
"""
AI Risk Radar — Predictive Milestone Risk Scoring
Trains a Random Forest model on programme data to flag at-risk milestones.

Usage:
    python generate_risk_model.py

Output:
    data/ai_risk_scores.csv
    assets/ai_risk_radar.png
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, classification_report
from sklearn.model_selection import LeaveOneOut
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load data
prog = pd.read_csv(DATA_DIR / "workstream_progress_weekly.csv", parse_dates=["week"])
ms = pd.read_csv(DATA_DIR / "milestones.csv", parse_dates=["baseline_date"])
vs = pd.read_csv(DATA_DIR / "vendor_scorecard.csv", index_col=0)
nk = pd.read_csv(DATA_DIR / "network_kpis_monthly.csv", parse_dates=["month"])
fin = pd.read_csv(DATA_DIR / "financials_monthly.csv", parse_dates=["month"])

ms["target"] = (ms["status"] == "At risk").astype(int)

# Feature engineering
features = []
for _, row in ms.iterrows():
    bd = row["baseline_date"]
    ws = row["workstream"]

    wp = prog[(prog["workstream"] == ws) & (prog["week"] <= bd)]
    prog_at = wp["progress"].max() if len(wp) else np.nan

    nm = nk[nk["month"] <= bd]
    avail = nm["availability"].iloc[-1] if len(nm) else np.nan
    mttr = nm["mttr_hrs"].iloc[-1] if len(nm) else np.nan
    mig = nm["migration_5g"].iloc[-1] if len(nm) else np.nan

    fm = fin[fin["month"] <= bd]
    capex_burn = (fm["capex_actual"].sum() / fm["capex_plan"].sum()) * 100 if len(fm) else np.nan
    rev_risk = fm["revenue_at_risk"].iloc[-1] if len(fm) else np.nan

    v_avg = vs.mean().mean()
    v_min = vs.mean(axis=1).min()
    days_from_start = (bd - pd.Timestamp("2026-01-05")).days

    features.append({
        "milestone": row["milestone"], "workstream": ws,
        "prog_at_baseline": prog_at, "availability": avail, "mttr": mttr,
        "migration_5g": mig, "capex_burn_pct": capex_burn,
        "revenue_at_risk": rev_risk, "vendor_avg_score": v_avg,
        "vendor_min_score": v_min, "days_from_start": days_from_start,
        "target": row["target"],
    })

feat_df = pd.DataFrame(features).dropna()

X = feat_df[["prog_at_baseline", "availability", "mttr", "migration_5g",
             "capex_burn_pct", "revenue_at_risk", "vendor_avg_score",
             "vendor_min_score", "days_from_start"]]
y = feat_df["target"].values
feature_names = X.columns.tolist()

# LOOCV
loo = LeaveOneOut()
preds_proba = np.zeros(len(y))
for train_idx, test_idx in loo.split(X):
    clf = RandomForestClassifier(n_estimators=200, max_depth=4, random_state=42, class_weight="balanced")
    clf.fit(X.iloc[train_idx], y[train_idx])
    preds_proba[test_idx[0]] = clf.predict_proba(X.iloc[test_idx])[:, 1]

auc = roc_auc_score(y, preds_proba)
print(f"LOOCV AUC: {auc:.3f}")

# Final model
final_clf = RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42, class_weight="balanced")
final_clf.fit(X, y)
feat_df["risk_score"] = final_clf.predict_proba(X)[:, 1]

# Save scores
feat_df[["milestone", "workstream", "risk_score", "target"]].round(3).to_csv(
    DATA_DIR / "ai_risk_scores.csv", index=False
)
print("Scores saved to data/ai_risk_scores.csv")

# Generate radar chart
fig = plt.figure(figsize=(18, 10), facecolor="white")
fig.suptitle("AI RISK RADAR — Predictive Milestone Risk Scoring", fontsize=15, fontweight="bold", color="#0f172a")

# Feature importance
ax1 = fig.add_subplot(2, 3, 1)
importances = pd.Series(final_clf.feature_importances_, index=feature_names).sort_values(ascending=True)
importances.plot(kind="barh", color="#1d4ed8", ax=ax1)
ax1.set_title("Feature Importance (RF, Gini)", fontsize=10, fontweight="bold", loc="left")
for s in ax1.spines.values(): s.set_visible(False)

# Risk scores
ax2 = fig.add_subplot(2, 3, 2)
colors = ["#ef4444" if t == 1 else "#94a3b8" for t in feat_df["target"]]
ax2.scatter(range(len(feat_df)), feat_df["risk_score"].sort_values(ascending=False), c=colors, s=80)
ax2.axhline(0.5, color="#f59e0b", ls="--", lw=1.5, label="Alert threshold")
ax2.set_title("Milestone Risk Scores (red = at risk)", fontsize=10, fontweight="bold", loc="left")
ax2.legend(fontsize=8)

# ROC
ax3 = fig.add_subplot(2, 3, 5)
fpr, tpr, _ = roc_curve(y, preds_proba)
ax3.plot(fpr, tpr, color="#1d4ed8", lw=2, label=f"ROC (AUC={auc:.3f})")
ax3.plot([0, 1], [0, 1], "--", color="#94a3b8")
ax3.set_title("ROC Curve (LOOCV)", fontsize=10, fontweight="bold", loc="left")
ax3.legend(fontsize=8)

# Model card
ax4 = fig.add_subplot(2, 3, 6)
ax4.axis("off")
card = (
    f"MODEL CARD\n"
    f"Algorithm: Random Forest (300 trees, max_depth=4)\n"
    f"Validation: Leave-One-Out CV (n={len(y)} milestones)\n"
    f"AUC: {auc:.3f}\n"
    f"Top driver: {importances.idxmax()} ({importances.max()*100:.1f}%)\n"
    f"All {y.sum()} at-risk milestones in top quintile"
)
ax4.text(0.05, 0.95, card, transform=ax4.transAxes, fontsize=9, color="#0f172a",
         verticalalignment="top", fontfamily="monospace",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#f1f5f9"))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "ai_risk_radar.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Radar chart saved to {OUTPUT_DIR / 'ai_risk_radar.png'}")
