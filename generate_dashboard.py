#!/usr/bin/env python3
"""
Network Transformation Command Centre — Dashboard Generator
Generates the executive programme & performance dashboard from synthetic data.

Usage:
    python generate_dashboard.py

Output:
    assets/dashboard_output.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------------
prog = pd.read_csv(DATA_DIR / "workstream_progress_weekly.csv", parse_dates=["week"])
ms = pd.read_csv(DATA_DIR / "milestones.csv")
nk = pd.read_csv(DATA_DIR / "network_kpis_monthly.csv", parse_dates=["month"])
fin = pd.read_csv(DATA_DIR / "financials_monthly.csv", parse_dates=["month"])
vs = pd.read_csv(DATA_DIR / "vendor_scorecard.csv", index_col=0)
rk = pd.read_csv(DATA_DIR / "risk_register.csv")
traj = pd.read_csv(DATA_DIR / "milestone_trajectory.csv")
scores = pd.read_csv(DATA_DIR / "ai_risk_scores.csv")

latest_nk = nk.iloc[-1]
latest_fin = fin.iloc[-1]

# ------------------------------------------------------------------
# BUILD DASHBOARD
# ------------------------------------------------------------------
fig = plt.figure(figsize=(20, 12), facecolor="#0b1220")
fig.suptitle(
    "NETWORK TRANSFORMATION COMMAND CENTRE — Executive Programme & Performance Dashboard",
    fontsize=15.5, fontweight="bold", color="white", y=0.98,
)
fig.text(
    0.5, 0.945,
    "Portfolio case study  •  Illustrative synthetic data  •  One-page board view  •  Monthly cadence, weekly flash",
    ha="center", fontsize=10, style="italic", color="#475569",
)

grid = fig.add_gridspec(3, 4, left=0.03, right=0.97, top=0.92, bottom=0.04, hspace=0.5, wspace=0.3)


def style_ax(ax, title):
    ax.set_facecolor("#16213a")
    ax.set_title(title, color="white", fontsize=10, fontweight="bold", loc="left", pad=8)
    ax.tick_params(colors="#94a3b8", labelsize=7)
    for s in ax.spines.values():
        s.set_color("#2c3d5e")


# Row 0, Col 0: Programme Health RAG
ax = fig.add_subplot(grid[0, 0])
style_ax(ax, "PROGRAMME HEALTH (RAG) — Month 11")
items = [
    ("WS1: 5G Core", "#22c55e"),
    ("WS2: Fibre Densif.", "#eab308"),
    ("WS3: OSS/BSS", "#ef4444"),
    ("WS4: Energy & Sust.", "#22c55e"),
    ("WS5: Automation", "#eab308"),
]
for i, (it, c) in enumerate(items):
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0.03, 0.86 - i * 0.19), 0.08, 0.11,
            boxstyle="round,pad=0.01", fc=c, ec="none", transform=ax.transAxes,
        )
    )
    ax.text(0.16, 0.915 - i * 0.19, it, transform=ax.transAxes, color="white", fontsize=7.8, va="center")
ax.axis("off")

# Row 0, Col 1: Milestone Trajectory
ax = fig.add_subplot(grid[0, 1])
style_ax(ax, "MILESTONE TRAJECTORY (cumulative % complete)")
ax.plot(traj["month"], traj["plan"], "--", color="#94a3b8", lw=1.5, label="Plan")
a = traj["actual"].dropna()
ax.plot(traj["month"][: len(a)], a, "-o", color="#38bdf8", lw=2, label="Actual")
ax.fill_between(traj["month"][: len(a)], a, traj["plan"][: len(a)], color="#ef4444", alpha=0.15)
ax.legend(facecolor="#16213a", labelcolor="white", fontsize=7, frameon=False)
ax.set_ylim(0, 105)

# Row 0, Col 2: Network Performance
ax = fig.add_subplot(grid[0, 2])
style_ax(ax, "NETWORK PERFORMANCE (latest vs target)")
labels = ["Availability\n%", "MTTR\n(hrs)", "Drop\nrate %", "5G migrate\n%"]
vals = [
    latest_nk["availability"],
    latest_nk["mttr_hrs"],
    latest_nk["drop_rate"],
    latest_nk["migration_5g"],
]
tgts = [99.98, 3.5, 1.5, 70]
cols = [
    "#22c55e" if vals[0] >= tgts[0] else "#ef4444",
    "#ef4444" if vals[1] > tgts[1] else "#22c55e",
    "#ef4444" if vals[2] > tgts[2] else "#22c55e",
    "#eab308" if vals[3] < tgts[3] else "#22c55e",
]
bars = ax.bar(labels, vals, color=cols, width=0.55)
for b, v, t in zip(bars, vals, tgts):
    ax.text(
        b.get_x() + b.get_width() / 2, b.get_height() + 1.3,
        f"{v}\n(t:{t})", ha="center", color="white", fontsize=6.8,
    )

# Row 0, Col 3: Financial Impact
ax = fig.add_subplot(grid[0, 3])
style_ax(ax, "FINANCIAL IMPACT — Month 11")
fl = ["Capex burn\nvs plan %", "Revenue at\nrisk S$M", "Savings run-\nrate S$M", "SLA penalties\nS$K"]
fv = [
    latest_fin["capex_actual"].sum() / latest_fin["capex_plan"].sum() * 100,
    latest_fin["revenue_at_risk"],
    latest_fin["savings_runrate"],
    latest_fin["sla_penalties"],
]
fc = ["#22c55e", "#ef4444", "#22c55e", "#eab308"]
bars = ax.barh(fl, fv, color=fc, height=0.5)
for b, v in zip(bars, fv):
    ax.text(v + 6, b.get_y() + b.get_height() / 2, f"{v:.0f}", va="center", color="white", fontsize=8.5, fontweight="bold")
ax.set_xlim(0, 560)

# Row 1, Col 0: Vendor Scorecard
ax = fig.add_subplot(grid[1, 0])
style_ax(ax, "VENDOR PERFORMANCE SCORECARD")
im = ax.imshow(vs.values, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")
ax.set_xticks(range(4), vs.columns, fontsize=7)
ax.set_yticks(range(4), vs.index, fontsize=7)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{vs.values[i, j]:.1f}", ha="center", va="center", fontsize=8.5, color="black", fontweight="bold")

# Row 1, Col 1: Risk Matrix
ax = fig.add_subplot(grid[1, 1])
style_ax(ax, "TOP RISKS (likelihood × impact)")
rm = np.array([[1, 2, 2, 3], [2, 3, 4, 4], [3, 4, 5, 5], [3, 4, 5, 5]])
ax.imshow(rm, cmap="RdYlGn_r", vmin=1, vmax=5, aspect="auto")
lik_map = {"Rare": 0, "Possible": 1, "Likely": 2, "Almost certain": 3}
imp_map = {"Minor": 0, "Moderate": 1, "Major": 2, "Severe": 3}
for _, r in rk.iterrows():
    y = lik_map[r["likelihood"]]
    x = imp_map[r["impact"]]
    ax.text(
        x, y, r["id"], ha="center", va="center", fontsize=8.5, fontweight="bold", color="white",
        bbox=dict(boxstyle="circle,pad=0.22", fc="#0b1220", ec="white", lw=0.8),
    )
ax.set_xticks(range(4), imp_map.keys(), fontsize=6.3)
ax.set_yticks(range(4), lik_map.keys(), fontsize=6.3)
ax.set_xlabel("Impact", color="#94a3b8", fontsize=7)
ax.set_ylabel("Likelihood", color="#94a3b8", fontsize=7)

# Row 1, Col 2-3: Roadmap
ax = fig.add_subplot(grid[1, 2:])
style_ax(ax, "CONSOLIDATED TRANSFORMATION ROADMAP (48-month horizon)")
phases = [
    ("Foundation\n(0-6m)", 0, 6, "#38bdf8"),
    ("Scale\n(6-18m)", 6, 18, "#818cf8"),
    ("Optimise & Automate\n(18-30m)", 18, 30, "#22c55e"),
    ("Monetise & AI-native\n(30-48m)", 30, 48, "#f59e0b"),
]
for i, (lab, s, e, c) in enumerate(phases):
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (s, i + 0.55), e - s, 0.8, boxstyle="round,pad=0.05", fc=c, ec="none", alpha=0.88,
        )
    )
    ax.text((s + e) / 2, i + 0.95, lab, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#0b1220")
for x, lab in [(6, "5G SA\nlaunch"), (18, "OSS/BSS cutover"), (30, "L3 auto\n40%"), (48, "AI-native\nmature")]:
    ax.axvline(x, color="#94a3b8", ls=":", lw=1)
    ax.text(x, 4.75, lab, ha="center", fontsize=6.5, color="#e2e8f0")
ax.set_xlim(0, 50)
ax.set_ylim(0, 5.5)
ax.set_yticks([])
ax.set_xlabel("Months", color="#94a3b8", fontsize=7)

# Row 2, Col 0-1: AI Insights
ax = fig.add_subplot(grid[2, 0:2])
style_ax(ax, "FORWARD-LOOKING INSIGHTS (predictive signals with recommended action)")
ins = [
    (
        "⚠",
        f"MTTR trending {latest_nk['mttr_hrs']:.1f}h vs {latest_nk['target_mttr']:.1f}h target — model predicts breach persists 8 weeks without spares pre-positioning in east clusters",
        "#f59e0b",
    ),
    (
        "✚",
        "Vendor Beta fibre-tranche velocity -2σ for 6 wks — recovery plan wk6; penalty clause invoked; M14 milestone watch",
        "#ef4444",
    ),
    (
        "↑",
        f"5G migration at {latest_nk['migration_5g']:.1f}% vs {latest_nk['target_migration']:.0f}% — on trajectory if device-bundle campaign launches Q1; anomaly model flags 2 clusters ahead",
        "#38bdf8",
    ),
    (
        "◆",
        "Shadow-mode AI risk scoring live: 78% of Month-10 slips flagged ≥3 weeks early — scale decision at Day-90 gate",
        "#22c55e",
    ),
]
for i, (ic, tx, c) in enumerate(ins):
    ax.text(0.02, 0.86 - i * 0.25, ic, transform=ax.transAxes, fontsize=11, color=c)
    ax.text(0.06, 0.86 - i * 0.25, tx, transform=ax.transAxes, fontsize=8, color="#e2e8f0", va="center")
ax.axis("off")

# Row 2, Col 2-3: BSC Summary
ax = fig.add_subplot(grid[2, 2:])
style_ax(ax, "BALANCED SCORECARD SUMMARY (leading + lagging, % of target)")
cats = ["Financial", "Customer", "Internal\nProcess", "Learning &\nGrowth"]
lead = [82, 74, 79, 71]
lag = [88, 77, 84, 75]
x = np.arange(4)
w = 0.35
ax.bar(x - w / 2, lead, w, label="Leading", color="#38bdf8")
ax.bar(x + w / 2, lag, w, label="Lagging", color="#818cf8")
for xi, (l, g) in enumerate(zip(lead, lag)):
    ax.text(xi - w / 2, l + 1.5, str(l), ha="center", color="white", fontsize=7)
    ax.text(xi + w / 2, g + 1.5, str(g), ha="center", color="white", fontsize=7)
ax.set_xticks(x, cats, fontsize=7)
ax.set_ylim(0, 100)
ax.set_ylabel("% of target", color="#94a3b8", fontsize=7)
ax.legend(facecolor="#16213a", labelcolor="white", fontsize=7, frameon=False, loc="lower right")

fig.text(
    0.03, 0.005,
    "Data: synthetic programme dataset (seed 42)  |  Freshness: T+1  |  Owner: Programme Management Office  |  Escalation: Programme Board → Steering → CTO",
    color="#64748b", fontsize=7,
)

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
plt.savefig(OUTPUT_DIR / "dashboard_output.png", dpi=150, bbox_inches="tight", facecolor="#0b1220")
plt.close()

print(f"Dashboard saved to {OUTPUT_DIR / 'dashboard_output.png'}")
