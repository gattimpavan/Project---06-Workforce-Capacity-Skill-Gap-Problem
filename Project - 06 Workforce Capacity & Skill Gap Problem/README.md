# Project - 06: Workforce Capacity & Skill Gap Problem

### Infosys Limited — AI Workforce Intelligence & Strategic Capacity Allocation System

---

## 📌 Problem Statement

> *"An Infosys company has sufficient employees on paper but continues to miss project deadlines because the required skills are not available at the right time. Develop an AI workforce intelligence system that maps employee skills against business requirements, identifies critical skill gaps, and recommends hiring, training and internal allocation strategies."*

---

## 🏢 Executive Solution Overview

Infosys Limited, employing over 300,000 technology and consulting professionals across five global Delivery Units (Financial Services, Retail & CPG, Manufacturing & Hi-Tech, Energy & Utilities, and Healthcare), operates under rigorous client contractual milestones and Service Level Agreements (SLAs). In recent quarters, despite reporting a healthy unassigned bench headcount (~16% on paper), multiple enterprise transformation projects have breached delivery deadlines and incurred severe contractual penalty deductions.

This project delivers an enterprise-grade **AI Workforce Intelligence & Strategic Capacity Allocation System** that dismantles the **"Paper Capacity Paradox"**, continuously maps talent competencies against business demands, predicts project deadline breaches, and formulates high-ROI prescriptive interventions across three operational pillars:

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │   INFOSYS WORKFORCE CAPACITY & SKILL GAP INTELLIGENCE       │
                               └──────────────────────────────┬──────────────────────────────┘
                                                              │
                    ┌─────────────────────────────────────────┴─────────────────────────────────────────┐
                    ▼                                                                                   ▼
      TALENT SUPPLY ENGINE (14,000 RECORDS)                                               BUSINESS DEMAND ENGINE (220 PROJECTS)
      • 25 Skills across 7 Tech Clusters                                                  • Required Primary Competency & Min Level
      • Validated Proficiency (L1 Novice -> L5 Expert)                                    • Staffing SLA Lead Time (7 - 60 Days)
      • Temporal Availability (Bench vs Rolling Release)                                  • Contract Value (₹ Cr) & Weekly SLA Penalty
      • Location Proximity & Mobility Readiness                                           • Allocated vs Unfulfilled Headcount Deficit
                    │                                                                                   │
                    └─────────────────────────────────────────┬─────────────────────────────────────────┘
                                                              │
                                                              ▼
                                   STRUCTURAL GAP IDENTIFICATION & ML PREDICTOR
                                   • The Paper Capacity Paradox Quantification
                                   • Skill Criticality Index (CI = Deficit × Scarcity × Revenue Exposure)
                                   • Gradient Boosting Deadline Breach Classifier (ROC-AUC: 0.9840)
                                                              │
                                                              ▼
                                   TRI-PILLAR STRATEGIC RECOMMENDATION ENGINE
              ┌───────────────────────────────────────────────┼───────────────────────────────────────────────┐
              ▼                                               ▼                                               ▼
     PILLAR 1: SMART BENCH MATCHING                 PILLAR 2: LEX ACCELERATED UPSKILLING             PILLAR 3: STRATEGIC EXTERNAL HIRE
     • Algorithmic Multi-Criteria Match             • Near-Neighbor Talent Bridging                  • Contingent Contractor Surge (<21d)
     • Match Score ≥75% & Available Now             • 14 - 28 Day Lex Sprints & Cloud Labs           • Lateral Permanent Hire (>35d)
     • Cost: ₹0.25L | Velocity: 3-5 Days            • Cost: ₹0.85L | Velocity: 14-28 Days            • Cost: ₹2.20L-₹2.80L | Velocity: 14-35d
```

---

## 📊 Key Results & Impact Benchmark

| Enterprise Metric | Status Quo (Spreadsheet RMG Allocation) | AI Workforce Intelligence System | Operational Delta / ROI |
| :--- | :--- | :--- | :--- |
| **Total Workforce Monitored** | 14,000 Employees | **14,000 Ingested Telemetry Records** | **100% Validated Skill Visibility** |
| **Gross Bench ('On Paper')** | 2,227 Engineers (15.9%) | **2,227 Monitored Bench Talent** | **Unveiled "Paper Capacity Paradox"** |
| **Legacy Bench Concentration** | 48.2% (1,073 in COBOL/Manual QA) | **Targeted for Lex Bridging** | **Identified Structural Asymmetry** |
| **Modern Cloud/AI Bench Rate** | < 2.8% Usable Bench | **Dynamic Rolling Pool Integration** | **+380% Available Modern Capacity** |
| **Project Deadline Breach Rate** | 32.27% of Projects (71 Breached) | **16.36% Post-Intervention (36 Residual)** | **-49.3% Breach Rate Reduction** |
| **SLA Delay Penalties Incurred** | ₹61.72 Crores Incurred | **₹17.22 Crores Residual Loss** | **Saved ₹44.50 Crores in Penalties** |
| **Total Intervention Investment** | ₹0.00 Cr (Passive Loss) | **₹1.47 - ₹1.85 Crores** | **High Capital Efficiency** |
| **Net Enterprise Financial Gain** | ₹0.00 Cr | **+₹43.03 Crores Net Savings** | **Portfolio ROI: 2,927%** |
| **Billable Bench Utilization** | 74.2% Base Utilization | **84.8% Simulated Utilization** | **+1,059 bps Utilization Gain** |

---

## 🧬 Understanding The "Paper Capacity Paradox"

The central research inquiry of this project addresses why an IT consulting giant can have **sufficient employees on paper** yet chronically miss enterprise project milestones:

### 1. Structural Skill Mismatch (Gross Supply vs Qualified Modern Demand)
* **Legacy Oversupply:** Over 48% of the unassigned bench is staffed with legacy competencies (COBOL, JCL, Manual Regression QA, Monolithic Java 7/8, On-prem DB Admin). These skill pools exhibit bench idling durations exceeding 90+ days.
* **Modern Deficit:** 84% of incoming client digital transformation projects demand Generative AI & LLMs, Databricks Lakehouse, Cloud Native Kubernetes (EKS/GKE), Golang Microservices, and SAP S/4HANA Cloud. The usable bench in these domains is virtually zero (<2.8%).

### 2. Temporal Latency & Release Timing
* Enterprise projects enforce kickoff deadlines within 7 to 28 days.
* High-performing modern engineers are billable on existing accounts with rolling releases 60 to 180 days out. High gross headcount numbers do not translate into immediate deployability.

### 3. Competency Depth & Resume Inflation
* Unvalidated keyword skills on employee profiles frequently mask proficiency deficits (Level 1 Novice vs Level 4 Lead Architect). Junior engineers placed on high-stakes projects without bridging support fail client technical screenings, deferring project delivery.

---

## 🤖 Machine Learning Predictive Modeling

A supervised **Gradient Boosting Classifier** evaluates multi-dimensional project signals to predict the probability of deadline breach prior to project kickoff:

$$P(\text{Breach}) = f(\text{Unfulfilled Ratio}, \text{Lead Urgency}, \text{Scarcity Index}, \text{SLA Penalty Exposure}, \text{Proficiency Threshold})$$

### Production Model Performance (Holdout Test Set)

* **Model Architecture:** Gradient Boosting Classifier (`n_estimators=100`, `learning_rate=0.08`, `max_depth=3`)
* **ROC-AUC Score:** **0.9840**
* **Classification Accuracy:** **96.4%**
* **Precision:** **94.4%**
* **Recall:** **94.4%**
* **F1-Score:** **0.9444**

### Feature Importance Weights
1. **Unfulfilled Ratio ($38.2\%$):** Percentage of unstaffed seats relative to total project staffing requirements.
2. **Skill Scarcity Index ($28.7\%$):** Industry talent scarcity of required technology cluster.
3. **Lead Urgency ($14.5\%$):** Inverse lead time before kickoff SLA deadline ($1 / \text{days}$).
4. **SLA Penalty Exposure ($9.8\%$):** Weekly financial penalty rate multiplied by unfulfilled seat gap.
5. **Required Minimum Proficiency ($5.4\%$):** Seniority requirement (Level 3 Practitioner vs Level 4 Architect).

---

## 🎯 The Tri-Pillar Optimization Framework

The system dynamically routes each open project seat through three decision pathways:

### Pillar 1: Smart Internal Allocation
* **Trigger:** Bench candidate or rolling-release employee within 15 days exhibits Match Score $\ge 75\%$.
* **Mechanism:** Algorithmic matching factoring skill overlap (45%), proficiency (25%), availability timeline (20%), and location mobility (10%).
* **Economics:** Cost = ₹25,000 (Transition onboarding) | Lead Time = 3-5 days | SLA Penalty Averted = 100%.

### Pillar 2: Accelerated Lex Upskilling
* **Trigger:** Candidate possesses adjacent "Near-Neighbor" skill (e.g., Python Developer $\rightarrow$ Databricks Data Engineer in 21 days; Core Java $\rightarrow$ Reactive Spring Boot in 20 days; Manual QA $\rightarrow$ Test Automation in 14 days) and bridge days $\le$ deadline days $+ 10$.
* **Mechanism:** Automated enrollment in curated Infosys Lex & Springboard learning cohorts, hands-on cloud labs, and pair-programming mentorship.
* **Economics:** Cost = ₹85,000 per engineer | Lead Time = 14-28 days | SLA Penalty Averted = 85-95%.

### Pillar 3: Strategic External Hiring
* **Trigger:** Zero internal bench and insufficient bridging runway before client SLA kickoff deadline.
* **Mechanism:**
  * *Contingent Contractor Surge:* Deployed for acute, short-lead (<21 days) demands to halt catastrophic weekly SLA penalty deductions.
  * *Lateral Permanent Staffing:* Deployed for multi-year recurring core technologies (e.g. GenAI Enterprise Architects, SAP S/4HANA Migration Leads).
* **Economics:** Cost = ₹2.2L - ₹2.8L | Lead Time = 14-35 days | SLA Penalty Averted = 90%.

---

## 🖥️ Interactive Web Dashboard & Architecture

The application provides a modern, obsidian dark glassmorphic web dashboard powered by Flask, Chart.js, and REST APIs:

* **Executive Overview Tab:** High-level enterprise KPIs, The Paper Capacity Paradox chart, and Delivery Unit SLA exposure.
* **Supply vs Demand Skill Gap Matrix:** Granular 25-skill table with cluster filtering, scarcity index, net capacity delta, and Criticality Score badges.
* **Tri-Pillar Strategic Recommender:** Project-by-project intervention decisions (`ALLOCATE`, `UPSKILL`, `HIRE`, `HYBRID`) with economic ROI.
* **Talent Matcher & Allocation Console:** Select any open client project to scan 14,000 employee records and review ranked candidate matches with detailed scoring breakdowns.
* **What-If Capacity Simulator:** Interactive sliders for Upskilling Velocity, Contractor Surge, Bench Cross-skilling, and Client SLA Buffer with live calculation of penalties saved and bench utilization.
* **Direct PDF Report Delivery:** Direct one-click download for the publication-grade PDF deliverable.

---

## 📄 Publication-Grade Executive PDF Report

A comprehensive 5-page publication-quality PDF deliverable is generated directly via ReportLab and Matplotlib:
* **Custom Numbered Canvas:** Running header rules and formal `"Page X of Y"` footers.
* **5 High-DPI Visualizations (DPI=240):**
  1. `chart1_paper_capacity_paradox.png`: Gross Bench vs Unfulfilled Project Demand.
  2. `chart2_deadline_breach_analysis.png`: Project Volume vs SLA Penalties across Delivery Units.
  3. `chart3_skill_criticality_matrix.png`: Top 8 Critical Skill Deficits causing project delays.
  4. `chart4_tripillar_allocation_strategy.png`: Fulfillment Channel Distribution & Net ROI Economics.
  5. `chart5_simulation_frontier_roi.png`: What-If Capacity Simulation Frontier.
* **Document Location:** `report/Infosys_Workforce_Capacity_Skill_Gap_Report.pdf` (758 KB).

---

## 🚀 How to Run the Project

### Prerequisites
* Python 3.10+
* Required packages: `flask`, `reportlab`, `matplotlib`, `scikit-learn`, `pandas`, `numpy`

### Quick Start (One-Click Master Orchestrator)
```powershell
# Navigate to the project root directory
cd "d:\Woxsen University\Trimester 4\AI Agents & Autonomous Business Operations\Practical Projects\Project - 06 Workforce Capacity & Skill Gap Problem"

# Run the master orchestrator
python run_project.py
```

### Accessing Deliverables
* **Interactive Web Dashboard:** Open your browser at [http://localhost:5006](http://localhost:5006)
* **Executive PDF Report:** Available at [http://localhost:5006/api/download_report](http://localhost:5006/api/download_report) or directly at `report/Infosys_Workforce_Capacity_Skill_Gap_Report.pdf`

