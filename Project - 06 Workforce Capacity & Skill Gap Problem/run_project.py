"""
Master One-Click Orchestrator for Project - 06: Workforce Capacity & Skill Gap Problem
Infosys Limited - Workforce Intelligence & Strategic Capacity Allocation System

Executes the complete end-to-end pipeline:
1. Ingests or generates 14,000 multi-dimensional Infosys workforce telemetry records.
2. Analyzes enterprise skill supply vs client project demand across 7 technology clusters.
3. Quantifies the 'Paper Capacity Paradox' (High gross bench vs acute digital skill deficits).
4. Trains a Gradient Boosting Machine Learning model predicting project deadline breaches (ROC-AUC ~0.98).
5. Generates the publication-grade executive PDF report with high-DPI Matplotlib visualizations.
6. Launches the interactive obsidian dark glassmorphic web dashboard at http://localhost:5006.
"""

import os
import sys
import webbrowser
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from data.generate_workforce_data import generate_workforce_dataset
from models.workforce_analyzer import WorkforceAnalyzer
from models.recommendation_engine import RecommendationEngine
from models.workforce_simulator import WorkforceSimulator
from report.generate_pdf_report import build_pdf_report

def main():
    print("=" * 85)
    print(" PROJECT - 06: WORKFORCE CAPACITY & SKILL GAP PROBLEM")
    print(" Infosys Limited - AI Workforce Intelligence & Strategic Capacity Allocation System")
    print("=" * 85)

    data_dir = os.path.join(base_dir, "data")
    tax_path = os.path.join(data_dir, "infosys_skill_taxonomy.csv")
    wf_path = os.path.join(data_dir, "infosys_workforce_inventory.csv")
    dm_path = os.path.join(data_dir, "infosys_project_demand.csv")
    pdf_path = os.path.join(base_dir, "report", "Infosys_Workforce_Capacity_Skill_Gap_Report.pdf")

    # Step 1: Data Ingestion & Verification
    print("\n[Step 1/5] Ingesting and verifying Infosys workforce telemetry datasets...")
    if not (os.path.exists(tax_path) and os.path.exists(wf_path) and os.path.exists(dm_path)):
        generate_workforce_dataset(data_dir)
    analyzer = WorkforceAnalyzer(data_dir)
    kpis = analyzer.get_executive_summary_kpis()
    print(f"  ✓ Ingested {kpis['total_workforce_headcount']:,} workforce records across 7 clusters.")
    print(f"  ✓ Active Bench: {kpis['gross_bench_headcount']:,} ({kpis['gross_bench_rate_pct']}%) | Legacy Bench Share: {kpis['legacy_bench_share_pct']}%.")
    print(f"  ✓ Client Projects Monitored: {kpis['total_client_projects']} | Breached: {kpis['projects_breached_count']} ({kpis['deadline_breach_rate_pct']}%).")
    print(f"  ✓ SLA Delay Penalties Incurred: ₹{kpis['total_sla_penalties_cr']:.2f} Crores.")

    # Step 2: Predictive Deadline Breach Modeling
    print("\n[Step 2/5] Training Gradient Boosting Machine Learning model for deadline breach prediction...")
    metrics = analyzer.train_deadline_predictor()
    print(f"  ✓ Production Model: {metrics['model_name']}")
    print(f"  ✓ Performance: ROC-AUC={metrics['roc_auc']} | Accuracy={metrics['accuracy']*100:.1f}% | F1={metrics['f1_score']}")

    # Step 3: Tri-Pillar Recommendation & Simulation Engines
    print("\n[Step 3/5] Initializing Tri-Pillar Recommendation Engine & Capacity Simulator...")
    engine = RecommendationEngine(analyzer.df_workforce, analyzer.df_demand, analyzer.df_taxonomy)
    sim = WorkforceSimulator(analyzer.df_workforce, analyzer.df_demand, analyzer.df_taxonomy)
    df_recs = engine.generate_project_recommendations()
    macro = engine.compute_macro_strategic_roi(df_recs)
    print(f"  ✓ Tri-Pillar Recommendations Formulated across {len(df_recs)} projects:")
    print(f"    • Internal Allocation: {macro['allocated_internal_headcount']} seats ({macro['internal_allocation_share_pct']}%)")
    print(f"    • Accelerated Lex Upskilling: {macro['upskilled_headcount']} seats ({macro['upskilling_share_pct']}%)")
    print(f"    • Strategic External Hiring: {macro['external_hired_headcount']} seats ({macro['external_hiring_share_pct']}%)")
    print(f"    • SLA Penalties Saved: ₹{macro['total_sla_penalties_saved_cr']:.2f} Cr | Portfolio ROI: {macro['macro_portfolio_roi_pct']}%")

    # Step 4: Executive PDF Report Generation
    print("\n[Step 4/5] Compiling publication-grade executive PDF report with high-DPI charts...")
    if not os.path.exists(pdf_path):
        build_pdf_report(analyzer, engine, sim, pdf_path)
    else:
        print(f"  ✓ Verified existing executive report: {pdf_path}")

    # Step 5: Web Dashboard Launch
    print("\n[Step 5/5] Launching interactive Infosys Workforce Intelligence Dashboard...")
    port = 5006
    url = f"http://localhost:{port}"
    print(f"\n" + "=" * 85)
    print(f"  DASHBOARD READY AT: {url}")
    print(f"  PDF REPORT AVAILABLE AT: {url}/api/download_report")
    print(f"  LOCAL PDF FILE PATH: {pdf_path}")
    print("=" * 85 + "\n")

    # Launch Flask App
    from app import app
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()

