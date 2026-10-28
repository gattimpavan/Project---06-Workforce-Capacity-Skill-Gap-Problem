"""
Flask Web Application for Project - 06: Workforce Capacity & Skill Gap Problem
Infosys Limited - Workforce Intelligence & Strategic Capacity Allocation System

Serves:
- Executive Glassmorphic Web Dashboard
- REST API endpoints for Supply-Demand diagnostics, Tri-Pillar recommendations, and ML predictions
- Interactive Multi-Criteria Talent Matcher for open client project demands
- Real-time What-If Capacity & Financial ROI Simulator
- Direct Publication-Grade PDF Report Delivery
"""

import os
import sys
import json
import pandas as pd
from flask import Flask, render_template, jsonify, request, send_file

# Add project root to path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from data.generate_workforce_data import generate_workforce_dataset
from models.workforce_analyzer import WorkforceAnalyzer
from models.recommendation_engine import RecommendationEngine
from models.talent_matcher import TalentMatcher
from models.workforce_simulator import WorkforceSimulator
from report.generate_pdf_report import build_pdf_report

app = Flask(__name__, static_folder="static", template_folder="templates")

# Paths configuration
DATA_DIR = os.path.join(base_dir, "data")
TAXONOMY_PATH = os.path.join(DATA_DIR, "infosys_skill_taxonomy.csv")
WORKFORCE_PATH = os.path.join(DATA_DIR, "infosys_workforce_inventory.csv")
DEMAND_PATH = os.path.join(DATA_DIR, "infosys_project_demand.csv")
REPORT_PATH = os.path.join(base_dir, "report", "Infosys_Workforce_Capacity_Skill_Gap_Report.pdf")

# Ensure dataset exists
if not (os.path.exists(TAXONOMY_PATH) and os.path.exists(WORKFORCE_PATH) and os.path.exists(DEMAND_PATH)):
    print("Generating comprehensive Infosys workforce telemetry datasets...")
    generate_workforce_dataset(DATA_DIR)

print("Initializing Workforce Analyzer and ML Models...")
analyzer = WorkforceAnalyzer(DATA_DIR)
analyzer.train_deadline_predictor()

print("Initializing Tri-Pillar Recommendation Engine and Talent Matcher...")
matcher = TalentMatcher(analyzer.df_workforce, analyzer.df_taxonomy)
engine = RecommendationEngine(analyzer.df_workforce, analyzer.df_demand, analyzer.df_taxonomy)
simulator = WorkforceSimulator(analyzer.df_workforce, analyzer.df_demand, analyzer.df_taxonomy)

# Cache precomputed recommendations for high-speed dashboard loading
cached_recommendations = engine.generate_project_recommendations()
cached_macro_roi = engine.compute_macro_strategic_roi(cached_recommendations)

# Ensure PDF report exists
if not os.path.exists(REPORT_PATH):
    print("Compiling publication-grade executive PDF report...")
    build_pdf_report(analyzer, engine, simulator, REPORT_PATH)

print("Infosys AI Workforce Intelligence System loaded successfully!")

@app.route("/")
def index():
    """Serves the main interactive Infosys Workforce Capacity Intelligence Dashboard."""
    return render_template("index.html")

@app.route("/api/summary")
def api_summary():
    """Returns global workforce statistics, project deadline breach telemetry, and ML model performance."""
    kpis = analyzer.get_executive_summary_kpis()
    kpis["ml_model_metrics"] = analyzer.model_metrics
    kpis["feature_importances"] = analyzer.feature_importances
    kpis["macro_roi"] = cached_macro_roi
    return jsonify({"status": "success", "data": kpis})

@app.route("/api/clusters")
def api_clusters():
    """Returns cluster-level analysis demonstrating the Paper Capacity Paradox."""
    df_paradox = analyzer.compute_cluster_level_paradox()
    return jsonify({"status": "success", "data": df_paradox.to_dict(orient="records")})

@app.route("/api/skills")
def api_skills():
    """Returns granular 25-skill supply-demand balance and Criticality Index ranking."""
    df_gaps = analyzer.compute_skill_level_gaps()
    return jsonify({"status": "success", "data": df_gaps.to_dict(orient="records")})

@app.route("/api/projects")
def api_projects():
    """Returns all client enterprise transformation projects with deadline telemetry."""
    du_filter = request.args.get("delivery_unit")
    breached_only = request.args.get("breached_only")

    df = analyzer.df_demand.copy()
    if du_filter and du_filter != "ALL":
        df = df[df["delivery_unit"] == du_filter]
    if breached_only and breached_only.lower() == "true":
        df = df[df["deadline_breached"] == 1]

    return jsonify({"status": "success", "count": len(df), "data": df.to_dict(orient="records")})

@app.route("/api/recommendations")
def api_recommendations():
    """Returns Tri-Pillar strategic recommendations (Allocate, Upskill, Hire) across open projects."""
    action_class = request.args.get("action_class")
    df = cached_recommendations.copy()

    if action_class and action_class != "ALL":
        df = df[df["action_class"] == action_class]

    return jsonify({
        "status": "success",
        "macro_roi": cached_macro_roi,
        "count": len(df),
        "data": df.to_dict(orient="records")
    })

@app.route("/api/match_talent", methods=["POST"])
def api_match_talent():
    """Finds top-ranked employee matches from bench and rolling-off talent for a specific project."""
    payload = request.get_json() or {}
    project_id = payload.get("project_id")

    if project_id:
        match_rows = analyzer.df_demand[analyzer.df_demand["project_id"] == project_id]
        if len(match_rows) > 0:
            prj_dict = match_rows.iloc[0].to_dict()
        else:
            return jsonify({"status": "error", "message": f"Project ID {project_id} not found"}), 404
    else:
        prj_dict = {
            "project_id": "CUSTOM-REQ",
            "required_skill": payload.get("required_skill", "GenAI & LLM Fine-Tuning"),
            "required_min_proficiency": int(payload.get("required_min_proficiency", 3)),
            "staffing_deadline_days": int(payload.get("staffing_deadline_days", 21)),
            "target_location": payload.get("target_location", "Bengaluru (Electronic City)"),
            "delivery_unit": payload.get("delivery_unit", "FS")
        }

    top_n = int(payload.get("top_n", 8))
    matches = matcher.find_matches_for_project(prj_dict, top_n=top_n)

    # Also compute ML breach risk for this project
    risk_info = analyzer.predict_project_risk(prj_dict)

    return jsonify({
        "status": "success",
        "project": prj_dict,
        "deadline_risk": risk_info,
        "matches_count": len(matches),
        "matches": matches
    })

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """Executes counterfactual capacity and policy simulation."""
    payload = request.get_json() or {}
    upskilling_velocity = float(payload.get("upskilling_velocity_pct", 25.0))
    contractor_surge = int(payload.get("contractor_surge_hc", 20))
    cross_skilling = float(payload.get("cross_skilling_mobilization", 20.0))
    sla_buffer = int(payload.get("sla_buffer_days", 7))

    sim_result = simulator.run_simulation(
        upskilling_velocity_pct=upskilling_velocity,
        contractor_surge_hc=contractor_surge,
        cross_skilling_mobilization=cross_skilling,
        sla_buffer_days=sla_buffer
    )

    return jsonify({"status": "success", "simulation": sim_result})

@app.route("/api/download_report")
def api_download_report():
    """Delivers the publication-grade executive PDF report."""
    if not os.path.exists(REPORT_PATH):
        build_pdf_report(analyzer, engine, simulator, REPORT_PATH)

    return send_file(
        REPORT_PATH,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Infosys_Workforce_Capacity_Skill_Gap_Report.pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    print(f"Starting Infosys Workforce Intelligence Dashboard on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)

