"""
Tri-Pillar Strategic Recommendation Engine (Internal Allocation, Training, External Hiring)
Project - 06: Workforce Capacity & Skill Gap Problem (Infosys Limited)

Automates prescriptive decision-making for open and unfulfilled client project requirements:
1. Pillar 1: Smart Internal Allocation (Immediate bench redeployment).
2. Pillar 2: Accelerated Upskilling / Lex Bridging Pathways (Near-neighbor talent reskilling).
3. Pillar 3: Strategic External Hiring (Contingent Contractor vs Lateral Hire).
"""

import os
import sys
import numpy as np
import pandas as pd
from models.talent_matcher import TalentMatcher

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class RecommendationEngine:
    def __init__(self, df_workforce: pd.DataFrame, df_demand: pd.DataFrame, df_taxonomy: pd.DataFrame):
        self.df_workforce = df_workforce
        self.df_demand = df_demand
        self.df_taxonomy = df_taxonomy
        self.matcher = TalentMatcher(df_workforce, df_taxonomy)
        self.taxonomy_map = {row["skill_name"]: row for _, row in df_taxonomy.iterrows()}

    def generate_project_recommendations(self, max_projects: int = None):
        """Generates comprehensive recommendations across all projects with unfulfilled headcount."""
        unfulfilled_prjs = self.df_demand[self.df_demand["unfulfilled_headcount"] > 0].copy()
        if max_projects:
            unfulfilled_prjs = unfulfilled_prjs.head(max_projects)

        recommendations = []

        for _, prj in unfulfilled_prjs.iterrows():
            prj_dict = prj.to_dict()
            unf_hc = int(prj["unfulfilled_headcount"])
            req_skill = prj["required_skill"]
            deadline_days = int(prj["staffing_deadline_days"])
            penalty_pw = float(prj["sla_penalty_per_week_lakhs"])
            potential_loss_lakhs = float(prj["sla_penalty_incurred_lakhs"]) if prj["deadline_breached"] else round(penalty_pw * 3.0, 2)
            
            tax_info = self.taxonomy_map.get(req_skill, {})
            bridge_from = tax_info.get("bridge_from", "Related Stack")
            bridge_days = int(tax_info.get("bridge_days", 21))
            scarcity = float(tax_info.get("scarcity", 0.8))

            # Query talent matcher for top internal matches
            matches = self.matcher.find_matches_for_project(prj_dict, top_n=6)
            
            # Categorize available matches
            deployable_internal = [m for m in matches if m["composite_match_score"] >= 78.0 and (
                m["allocation_status"] == "Active_Bench" or 
                (m["allocation_status"] == "Billed_Project" and "On Time" in m["availability_description"])
            )]
            
            bridgeable_internal = [m for m in matches if 60.0 <= m["composite_match_score"] < 78.0 or (
                bridge_days <= deadline_days + 10 and m["composite_match_score"] >= 55.0
            )]

            # Allocation Plan logic
            allocated_internal_hc = min(unf_hc, len(deployable_internal))
            remaining_after_alloc = unf_hc - allocated_internal_hc

            upskill_hc = 0
            if remaining_after_alloc > 0:
                if bridge_days <= deadline_days + 7 and len(bridgeable_internal) > 0:
                    upskill_hc = min(remaining_after_alloc, len(bridgeable_internal))
            remaining_after_upskill = remaining_after_alloc - upskill_hc

            external_hire_hc = remaining_after_upskill

            # Primary Strategy Decision
            if allocated_internal_hc == unf_hc:
                primary_strategy = "Internal Bench Allocation"
                action_class = "ALLOCATE"
                urgency = "Moderate"
                lead_time_days = 5
                cost_lakhs = round(allocated_internal_hc * 0.25, 2)
                sla_saved_lakhs = potential_loss_lakhs
                details = f"Identified {allocated_internal_hc} qualified bench engineers with average match score {np.mean([m['composite_match_score'] for m in deployable_internal[:allocated_internal_hc]]):.1f}%. Immediate redeployment feasible within 5 days."
            elif allocated_internal_hc > 0 and (upskill_hc > 0 or external_hire_hc > 0):
                primary_strategy = "Hybrid Internal Allocation & Bridging"
                action_class = "HYBRID"
                urgency = "High" if deadline_days <= 21 else "Medium"
                lead_time_days = max(5, bridge_days if upskill_hc > 0 else 18)
                cost_lakhs = round(allocated_internal_hc * 0.25 + upskill_hc * 0.85 + external_hire_hc * 2.80, 2)
                sla_saved_lakhs = round(potential_loss_lakhs * 0.88, 2)
                details = f"Redeploy {allocated_internal_hc} from bench; fast-track {upskill_hc} engineers via {bridge_days}-day Lex bridging cohort from '{bridge_from}'; source {external_hire_hc} via external partner."
            elif upskill_hc > 0 and external_hire_hc == 0:
                primary_strategy = "Targeted Accelerated Upskilling"
                action_class = "UPSKILL"
                urgency = "High" if deadline_days <= 21 else "Medium"
                lead_time_days = bridge_days
                cost_lakhs = round(upskill_hc * 0.85, 2) # ₹85,000 per reskilled engineer
                sla_saved_lakhs = round(potential_loss_lakhs * 0.85, 2)
                details = f"No ready bench found. Enroll {upskill_hc} bench candidates in {bridge_days}-day intensive Lex Sprint for '{req_skill}' bridged from '{bridge_from}' with hands-on labs."
            else:
                # External hiring required
                is_urgent = (deadline_days <= 25)
                hire_channel = "Contingent Contractor Surge" if is_urgent else "Lateral Strategic Hire"
                primary_strategy = f"External Staffing ({hire_channel})"
                action_class = "HIRE"
                urgency = "Critical" if is_urgent else "High"
                lead_time_days = 14 if is_urgent else 35
                cost_lakhs = round(external_hire_hc * (2.80 if is_urgent else 2.20), 2)
                sla_saved_lakhs = round(potential_loss_lakhs * 0.90, 2)
                details = f"Zero viable internal bench or bridging runway before deadline ({deadline_days}d). Initiate {hire_channel} for {external_hire_hc} specialists in '{req_skill}'."

            net_roi = round(float((sla_saved_lakhs - cost_lakhs) / max(0.1, cost_lakhs) * 100), 1)

            recommendations.append({
                "project_id": prj["project_id"],
                "project_name": prj["project_name"],
                "client_name": prj["client_name"],
                "delivery_unit": prj["delivery_unit"],
                "required_skill": req_skill,
                "skill_cluster": prj["skill_cluster"],
                "unfulfilled_headcount": unf_hc,
                "staffing_deadline_days": deadline_days,
                "deadline_breached": int(prj["deadline_breached"]),
                "potential_sla_loss_lakhs": potential_loss_lakhs,
                "primary_strategy": primary_strategy,
                "action_class": action_class,
                "urgency": urgency,
                "allocated_internal_hc": allocated_internal_hc,
                "upskill_hc": upskill_hc,
                "external_hire_hc": external_hire_hc,
                "estimated_lead_time_days": lead_time_days,
                "estimated_cost_lakhs": cost_lakhs,
                "sla_penalty_saved_lakhs": sla_saved_lakhs,
                "net_roi_pct": net_roi,
                "strategic_action_summary": details,
                "top_candidate_preview": [
                    {
                        "id": m["employee_id"],
                        "name": m["full_name"],
                        "match_score": m["composite_match_score"],
                        "status": m["allocation_status"],
                        "tier": m["fit_tier"]
                    } for m in matches[:3]
                ]
            })

        df_rec = pd.DataFrame(recommendations)
        return df_rec

    def compute_macro_strategic_roi(self, df_rec: pd.DataFrame = None):
        """Computes aggregate enterprise financial and capacity ROI from implementing the Tri-Pillar recommendations."""
        if df_rec is None:
            df_rec = self.generate_project_recommendations()

        total_open_hc = int(df_rec["unfulfilled_headcount"].sum())
        total_internal_alloc = int(df_rec["allocated_internal_hc"].sum())
        total_upskill = int(df_rec["upskill_hc"].sum())
        total_hire = int(df_rec["external_hire_hc"].sum())

        total_cost_cr = round(float(df_rec["estimated_cost_lakhs"].sum() / 100.0), 2)
        total_penalties_saved_cr = round(float(df_rec["sla_penalty_saved_lakhs"].sum() / 100.0), 2)
        net_financial_gain_cr = round(float(total_penalties_saved_cr - total_cost_cr), 2)
        portfolio_roi_pct = round(float((net_financial_gain_cr / max(0.1, total_cost_cr)) * 100), 1)

        # Impact on project deadline breaches
        initial_breached_count = int(self.df_demand["deadline_breached"].sum())
        # With recommendations: internal allocation and rapid contractor surge avert breaches
        averted_breaches = int((df_rec["estimated_lead_time_days"] <= df_rec["staffing_deadline_days"] + 5).sum())
        residual_breaches = max(0, initial_breached_count - averted_breaches)
        breach_reduction_pct = round(((initial_breached_count - residual_breaches) / max(1, initial_breached_count)) * 100, 1)

        return {
            "total_unfulfilled_headcount": total_open_hc,
            "allocated_internal_headcount": total_internal_alloc,
            "internal_allocation_share_pct": round((total_internal_alloc / max(1, total_open_hc)) * 100, 1),
            "upskilled_headcount": total_upskill,
            "upskilling_share_pct": round((total_upskill / max(1, total_open_hc)) * 100, 1),
            "external_hired_headcount": total_hire,
            "external_hiring_share_pct": round((total_hire / max(1, total_open_hc)) * 100, 1),
            "total_implementation_cost_cr": total_cost_cr,
            "total_sla_penalties_saved_cr": total_penalties_saved_cr,
            "net_financial_benefit_cr": net_financial_gain_cr,
            "macro_portfolio_roi_pct": portfolio_roi_pct,
            "initial_breached_projects": initial_breached_count,
            "averted_breached_projects": averted_breaches,
            "residual_breached_projects": residual_breaches,
            "deadline_breach_reduction_pct": breach_reduction_pct
        }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    tax = pd.read_csv(os.path.join(data_dir, "infosys_skill_taxonomy.csv"))
    wf = pd.read_csv(os.path.join(data_dir, "infosys_workforce_inventory.csv"))
    dm = pd.read_csv(os.path.join(data_dir, "infosys_project_demand.csv"))

    engine = RecommendationEngine(wf, dm, tax)
    df_recs = engine.generate_project_recommendations()
    macro = engine.compute_macro_strategic_roi(df_recs)
    print("Macro Recommendations ROI:", macro)

