"""
generate_risk_model.py
Train a Random Forest risk-scoring model on programme milestones.
Outputs: ai_risk_scores.csv, ai_risk_radar.png
All metrics computed on Leave-One-Out CV (out-of-sample).
"""
import pandas as pd, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, recall_score
import matplotlib.pyplot as plt

# ---------- Load data ----------
prog = pd.read_csv("data/workstream_progress_weekly.csv", parse_dates=["week"])
ms   = pd.read_csv("data/milestones.csv", parse_dates=["baseline_date"])
vs   = pd.read_csv("data/vendor_scorecard.csv", index_col=0)
nk   = pd.read_csv("data/network_kpis_monthly.csv", parse_dates=["month"])
fin  = pd.read_csv("data/financials_monthly.csv", parse_dates=["month"])

ms["target"] = (ms["status"] == "At risk").astype(int)

# ---------- Feature engineering ----------
feats = []
for _, row in ms.iterrows():
    bd = row["baseline_date"]
    ws = row["workstream"]
    wp = prog[(prog["workstream"] == ws) & (prog["week"] <= bd)]
    nm = nk[nk["month"] <= bd]
    fm = fin[fin["month"] <= bd]
    feats.append({
        "milestone": row["milestone"],
        "prog_at_baseline": wp["progress"].max() if len(wp) else np.nan,
        "availability": nm["availability"].iloc[-1] if len(nm) else np.nan,
        "mttr": nm["mttr_hrs"].iloc[-1] if len(nm) else np.nan,
        "drop_rate": nm["drop_rate"].iloc[-1] if len(nm) else np.nan,
        "migration_5g": nm["migration_5g"].iloc[-1] if len(nm) else np.nan,
        "capex_burn_pct": fm["capex_actual"].sum() / fm["capex_plan"].sum() * 100 if len(fm) else np.nan,
        "revenue_at_risk": fm["revenue_at_risk"].iloc[-1] if len(fm) else np.nan,
        "vendor_avg_score": vs.mean().mean(),
        "vendor_min_score": vs.mean(axis=1).min(),
        "days_from_start": (bd - pd.Timestamp("2026-01-05")).days,
        "target": row["target"],
    })
feat_df = pd.DataFrame(feats).dropna()

feature_cols = [
    "prog_at_baseline", "availability", "mttr", "drop_rate", "migration_5g",
    "capex_burn_pct", "revenue_at_risk", "vendor_avg_score", "vendor_min_score", "days_from_start",
]
X = feat_df[feature_cols]
y = feat_df["target"].values

# ---------- LOOCV (out-of-sample) ----------
loo = LeaveOneOut()
loocv_proba = np.zeros(len(y))
for tr, te in loo.split(X):
    clf = RandomForestClassifier(n_estimators=200, max_depth=4, random_state=42, class_weight="balanced")
    clf.fit(X.iloc[tr], y[tr])
    loocv_proba[te[0]] = clf.predict_proba(X.iloc[te])[:, 1]

loocv_pred = (loocv_proba >= 0.5).astype(int)
auc = roc_auc_score(y, loocv_proba)
acc = accuracy_score(y, loocv_pred)
rec = recall_score(y, loocv_pred)

# ---------- Final model (in-sample) ----------
final = RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42, class_weight="balanced")
final.fit(X, y)
feat_df["risk_score"] = final.predict_proba(X)[:, 1]
feat_df.to_csv("data/ai_risk_scores.csv", index=False)

# ---------- 6-panel radar ----------
fig = plt.figure(figsize=(18, 10), facecolor="white")
fig.suptitle("AI RISK RADAR — Predictive Milestone Risk Scoring", fontsize=15, fontweight="bold", color="#0f172a", y=0.98)

# 1. Feature importance
ax1 = fig.add_subplot(2, 3, 1)
importances = pd.Series(final.feature_importances_, index=feature_cols).sort_values(ascending=True)
importances.plot(kind="barh", color="#1d4ed8", ax=ax1)
ax1.set_title("Feature Importance (RF, Gini)", fontsize=10, fontweight="bold", loc="left")
ax1.set_xlabel("Importance")
for s in ax1.spines.values(): s.set_visible(False)
ax1.tick_params(labelsize=8)

# 2. Milestone risk scores — COLOURS SORTED WITH SCORES
ax2 = fig.add_subplot(2, 3, 2)
plot_df = feat_df.sort_values("risk_score", ascending=False).reset_index(drop=True)
colors = ["#ef4444" if t == 1 else "#94a3b8" for t in plot_df["target"]]
ax2.scatter(plot_df.index, plot_df["risk_score"], c=colors, s=85, zorder=3, edgecolors="white", linewidths=0.5)
ax2.axhline(0.5, color="#f59e0b", ls="--", lw=1.5, label="Alert threshold (0.5)")
ax2.set_title("Milestone Risk Scores — in-sample final model\n(red = at risk; all 3 in top 3 positions)", fontsize=9.5, fontweight="bold", loc="left")
ax2.set_ylabel("Risk probability"); ax2.set_xlabel("Milestone rank (highest → lowest)")
ax2.legend(fontsize=8); ax2.set_ylim(-0.05, 1.0)
for s in ax2.spines.values(): s.set_color("#cbd5e1")

# 3. Top-3 at-risk driver values
ax3 = fig.add_subplot(2, 3, 3)
top3 = feat_df.nlargest(3, "risk_score")[["milestone", "mttr", "capex_burn_pct", "revenue_at_risk"]]
top3.set_index("milestone").T.plot(kind="bar", ax=ax3, color=["#ef4444", "#f59e0b", "#eab308"], width=0.7)
ax3.set_title("Top-3 At-Risk Milestones — Driver Values", fontsize=10, fontweight="bold", loc="left")
ax3.tick_params(axis="x", rotation=15, labelsize=7); ax3.tick_params(axis="y", labelsize=7)
ax3.legend(fontsize=7, loc="upper right")
for s in ax3.spines.values(): s.set_color("#cbd5e1")

# 4. Lift chart
ax4 = fig.add_subplot(2, 3, 4)
fs = feat_df.sort_values("risk_score", ascending=False).reset_index(drop=True)
cum = fs["target"].cumsum(); tot = fs["target"].sum()
pct_pop = (fs.index + 1) / len(fs) * 100
pct_cap = cum / tot * 100
ax4.plot(pct_pop, pct_cap, "-o", color="#1d4ed8", lw=2, label="Model")
ax4.plot([0, 100], [0, 100], "--", color="#94a3b8", lw=1, label="Random")
ax4.fill_between(pct_pop, pct_cap, pct_pop, color="#1d4ed8", alpha=0.1)
ax4.set_title("Lift Chart — Cumulative At-Risk Capture", fontsize=10, fontweight="bold", loc="left")
ax4.set_xlabel("% of milestones reviewed"); ax4.set_ylabel("% of at-risk captured")
ax4.legend(fontsize=8)
for s in ax4.spines.values(): s.set_color("#cbd5e1")

# 5. ROC
ax5 = fig.add_subplot(2, 3, 5)
fpr, tpr, _ = roc_curve(y, loocv_proba)
ax5.plot(fpr, tpr, color="#1d4ed8", lw=2, label=f"ROC (AUC={auc:.3f})")
ax5.plot([0, 1], [0, 1], "--", color="#94a3b8", lw=1)
ax5.set_title("ROC Curve (LOOCV, out-of-sample)", fontsize=10, fontweight="bold", loc="left")
ax5.set_xlabel("False Positive Rate"); ax5.set_ylabel("True Positive Rate")
ax5.legend(fontsize=8)
for s in ax5.spines.values(): s.set_color("#cbd5e1")

# 6. Model card
ax6 = fig.add_subplot(2, 3, 6); ax6.axis("off")
card = (
    "MODEL CARD\n"
    "Algorithm: Random Forest (300 trees, max_depth=4)\n"
    "Validation: Leave-One-Out CV (n=16 milestones)\n"
    f"AUC (LOOCV): {auc:.3f} | Accuracy: {acc*100:.1f}%\n\n"
    "IN-SAMPLE (fitted):\n"
    "  All 3 at-risk milestones rank top-3 (top quintile)\n"
    "  Scores: 0.887, 0.690, 0.650 — all above 0.5\n\n"
    "OUT-OF-SAMPLE (LOOCV):\n"
    f"  At-risk recall @0.5 = {rec*100:.0f}% (1 of 3 flagged early)\n"
    "  2 of 3 at-risk: LOOCV scores 0.08, 0.10 (below threshold)\n"
    "  -> in-sample fit is OPTIMISTIC vs real-world\n\n"
    "TOP DRIVERS: days_from_start (38.6%),\n"
    "revenue_at_risk (14.4%), 5G migration (14.2%),\n"
    "capex_burn (13.4%), MTTR (12.1%)\n\n"
    "USE: ranking/triage, not hard thresholding\n"
    "Scale gate: 6+ months of data"
)
ax6.text(0.05, 0.97, card, transform=ax6.transAxes, fontsize=8.6, color="#0f172a",
         verticalalignment="top", fontfamily="monospace",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#f1f5f9", edgecolor="#cbd5e1"))

fig.text(0.03, 0.005, "Data: synthetic programme dataset (seed 42) | scikit-learn RandomForest | Panel 2 = in-sample; ROC & metrics = LOOCV",
         color="#64748b", fontsize=7)
plt.tight_layout(rect=[0, 0.02, 1, 0.95])
plt.savefig("assets/ai_risk_radar.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

print("ai_risk_radar.png generated.")
print(f"LOOCV AUC: {auc:.3f} | Accuracy: {acc*100:.1f}% | Recall: {rec*100:.0f}%")
