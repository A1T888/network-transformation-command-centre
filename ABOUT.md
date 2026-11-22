# About

This portfolio presents a complete programme governance and performance measurement system for a large-scale network transformation — built as a demonstrable case study in programme management, business planning, and AI-enabled performance analytics.

## Scope

A simulated 30-month network transformation programme covering five interdependent workstreams:

- **5G Core Modernisation** — SA core design, lab validation, commercial launch, VoNR enablement
- **Fibre Densification** — PoP augmentation, node deployment across two tranches
- **OSS/BSS Transformation** — inventory consolidation, billing migration (two waves)
- **Energy & Sustainability** — baseline audit, solar deployment, AI-driven optimisation
- **Network Automation** — L1 playbook, L2 coverage, L3 automation target

## What is demonstrated

### 1. Performance Architecture
A 23-KPI framework built on a Balanced Scorecard spine, with leading and lagging indicators paired across four perspectives (Financial, Customer, Internal Process, Learning & Growth). Every technical metric carries a financial translation. The board view is capped at 10 standing KPIs with a published reserve list.

### 2. Executive Reporting
A one-page dashboard designed for boardroom consumption: programme health RAG, milestone trajectory, network KPIs vs target, financial impact, vendor scorecard, risk heatmap, transformation roadmap, forward-looking AI insights, and BSC summary. Each tile includes a forecast and a recommended action.

### 3. Predictive Analytics
A Random Forest risk-scoring model (AUC = 0.846, LOOCV) trained on programme data to flag at-risk milestones early. Shadow-mode validation: 78% of historical slips flagged ≥3 weeks before external signs appeared. All AI use cases carry baseline measurements, total cost of AI (TCA) tracking, and scale/stop gates.

### 4. Vendor Management
Vendor scorecards (4 vendors × 4 dimensions), shadow-to-live cycles, penalty clauses tied to contract terms, quarterly business reviews with improvement plans, and business impact assessments on late delivery.

### 5. Governance Design
Six forums with defined inputs/outputs, a 4-level escalation matrix with SLAs, RAPID decision rights, decision-only agendas, a cancel-if-no-decision rule, and a standing blocker watchlist (B1–B10) reviewed weekly.

## Methodology

- **KPI selection:** 7-step method — strategy map → KPA → SMART filter → few-but-powerful cull → baseline/target → owner/data contract → MPRA (Measure-Perform-Review-Adapt) rhythm
- **AI governance:** Baseline ≥4 weeks before build; hard/soft value separation; scale/stop gates (≥2.0x net value); CISO review in week 1; human-in-the-loop for vendor/customer/spend decisions
- **Data:** Fully reproducible synthetic dataset (numpy seed 42). Every dashboard number traces to a CSV row.

## Key results (Month 11)

| Dimension | Outcome |
|---|---|
| Programme health | 3 Green, 2 Amber, 1 Red (OSS/BSS wave 2 at risk) |
| Milestone trajectory | 88% actual vs 92% plan — 3 milestones with named recovery plans |
| Network | Availability 99.99% (Green); MTTR 4.51h (Red); 5G migration 66.3% (Amber) |
| Financial | Revenue at risk halved (S$24M → S$12.6M); savings run-rate S$39.8M; capex 98% of plan |
| AI | All 3 at-risk milestones in top risk quintile; AUC = 0.846 |

---

*All data is synthetic and generated for portfolio demonstration purposes. No real employer or programme data is used.*
