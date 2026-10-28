"""
Counterfactual What-If Capacity & Skill Gap Simulator
Project - 06: Workforce Capacity & Skill Gap Problem (Infosys Limited)

Simulates the macroeconomic impact of strategic interventions:
1. Upskilling Velocity Boost (Accelerating Lex bridging completion rates).
2. Contractor Contingent Surge (Injecting external niche specialists).
3. Cross-Skilling Mobilization (Pairing adjacent bench engineers with lead architects).
4. Client SLA Buffer Window (Negotiating delivery milestone tolerances).
"""

import os
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class WorkforceSimulator:
    def __init__(self, df_workforce: pd.DataFrame, df_demand: pd.DataFrame, df_taxonomy: pd.DataFrame):
        self.df_workforce = df_workforce
        self.df_demand = df_demand
        self.df_taxonomy = df_taxonomy

    def run_simulation(
        self,
        upskilling_velocity_pct: float = 25.0,     # 0% to 50% faster upskilling
        contractor_surge_hc: int = 25,             # 0 to 60 contractor specialists
        cross_skilling_mobilization: float = 20.0, # 0% to 40% increased bench redeployment
        sla_buffer_days: int = 7                   # 0 to 21 additional grace days
    ):
        """Simulates counterfactual workforce outcomes based on adjustable policy levers."""
        base_df = self.df_demand.copy()
        
        baseline_breaches = int(base_df["deadline_breached"].sum())
        baseline_penalties_cr = round(float(base_df["sla_penalty_incurred_lakhs"].sum() / 100.0), 2)
        total_projects = len(base_df)

        # Baseline bench telemetry
        total_bench = len(self.df_workforce[self.df_workforce["allocation_status"] == "Active_Bench"])
        modern_clusters = ["Generative AI & ML", "Cloud Native & DevOps", "Modern Data & Analytics"]
        baseline_modern_bench = len(self.df_workforce[
            (self.df_workforce["allocation_status"] == "Active_Bench") &
            (self.df_workforce["skill_cluster"].isin(modern_clusters))
        ])

        # Counterfactual transformation per project
        sim_breaches = 0
        sim_penalties_lakhs = 0.0
        contingent_remaining = contractor_surge_hc

        simulated_projects = []

        for _, prj in base_df.iterrows():
            req_hc = prj["required_headcount"]
            allocated_hc = prj["allocated_headcount"]
            unf_hc = prj["unfulfilled_headcount"]
            deadline_days = prj["staffing_deadline_days"] + sla_buffer_days
            scarcity = prj["skill_scarcity_index"]
            penalty_pw = prj["sla_penalty_per_week_lakhs"]
            was_breached = bool(prj["deadline_breached"])

            if unf_hc == 0:
                simulated_projects.append({"project_id": prj["project_id"], "sim_breached": 0, "sim_penalty_lakhs": 0.0})
                continue

            # Step 1: Benefit from cross-skilling mobilization (adjacent bench deployed with shadow support)
            cross_skill_gain = int(np.floor(unf_hc * (cross_skilling_mobilization / 100.0) * (1.2 - scarcity)))
            unf_hc = max(0, unf_hc - cross_skill_gain)

            # Step 2: Benefit from accelerated upskilling velocity
            if unf_hc > 0 and deadline_days >= 14:
                upskill_gain = int(np.floor(unf_hc * (upskilling_velocity_pct / 100.0)))
                unf_hc = max(0, unf_hc - upskill_gain)

            # Step 3: Benefit from contractor surge
            if unf_hc > 0 and contingent_remaining > 0:
                surge_allocated = min(unf_hc, contingent_remaining)
                contingent_remaining -= surge_allocated
                unf_hc = max(0, unf_hc - surge_allocated)

            # Re-evaluate breach condition under new simulated state
            unfilled_ratio = unf_hc / max(1, req_hc)
            sim_breach_prob = (unfilled_ratio * 0.50) + (scarcity * 0.35) + (0.25 if deadline_days <= 14 else 0.10 if deadline_days <= 28 else 0.0)
            
            # Simulated breach status
            is_sim_breach = 1 if (unf_hc > 0 and (sim_breach_prob > 0.65 or (unfilled_ratio >= 0.30 and deadline_days <= 21))) else 0

            if is_sim_breach:
                sim_breaches += 1
                # Delay days reduced due to buffers and partial fills
                sim_delay = max(7, int(prj["actual_delay_days"] * 0.60) if prj["actual_delay_days"] > 0 else 14)
                sim_pen = round(float((sim_delay / 7.0) * penalty_pw), 2)
                sim_penalties_lakhs += sim_pen
            else:
                sim_pen = 0.0

            simulated_projects.append({
                "project_id": prj["project_id"],
                "sim_breached": is_sim_breach,
                "sim_penalty_lakhs": sim_pen
            })

        sim_penalties_cr = round(float(sim_penalties_lakhs / 100.0), 2)
        penalties_saved_cr = round(float(baseline_penalties_cr - sim_penalties_cr), 2)
        breaches_averted = baseline_breaches - sim_breaches
        breach_reduction_pct = round((breaches_averted / max(1, baseline_breaches)) * 100, 1)

        # Economic calculation of interventions:
        # Upskilling cost: ~₹75,000 per reskilled engineer
        # Contractor cost: ~₹3,20,000 per contractor
        # Shadow pairing cost: ~₹35,000 per pair
        upskilling_investment_cr = round(float((upskilling_velocity_pct / 100.0) * 180 * 0.75 / 100.0), 2)
        contractor_investment_cr = round(float((contractor_surge_hc - contingent_remaining) * 3.20 / 100.0), 2)
        cross_skill_investment_cr = round(float((cross_skilling_mobilization / 100.0) * 120 * 0.35 / 100.0), 2)
        total_intervention_cost_cr = round(float(upskilling_investment_cr + contractor_investment_cr + cross_skill_investment_cr), 2)

        net_savings_cr = round(float(penalties_saved_cr - total_intervention_cost_cr), 2)
        simulation_roi_pct = round(float((net_savings_cr / max(0.1, total_intervention_cost_cr)) * 100), 1)

        # Usable bench utilization improvement
        baseline_utilization = 74.2
        redeployed_bench_count = int(total_bench * (cross_skilling_mobilization / 200.0))
        simulated_utilization = round(min(92.5, baseline_utilization + (redeployed_bench_count / total_bench) * 100 * 0.85), 1)

        return {
            "simulation_parameters": {
                "upskilling_velocity_pct": upskilling_velocity_pct,
                "contractor_surge_hc": contractor_surge_hc,
                "cross_skilling_mobilization": cross_skilling_mobilization,
                "sla_buffer_days": sla_buffer_days
            },
            "baseline": {
                "breached_projects": baseline_breaches,
                "breach_rate_pct": round((baseline_breaches / total_projects) * 100, 1),
                "total_penalties_cr": baseline_penalties_cr,
                "bench_utilization_pct": baseline_utilization
            },
            "simulated": {
                "breached_projects": sim_breaches,
                "breach_rate_pct": round((sim_breaches / total_projects) * 100, 1),
                "total_penalties_cr": sim_penalties_cr,
                "bench_utilization_pct": simulated_utilization
            },
            "impact": {
                "breaches_averted": breaches_averted,
                "breach_reduction_pct": breach_reduction_pct,
                "sla_penalties_saved_cr": penalties_saved_cr,
                "total_intervention_cost_cr": total_intervention_cost_cr,
                "net_financial_savings_cr": net_savings_cr,
                "simulation_roi_pct": simulation_roi_pct,
                "utilization_gain_bps": int((simulated_utilization - baseline_utilization) * 100)
            }
        }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    tax = pd.read_csv(os.path.join(data_dir, "infosys_skill_taxonomy.csv"))
    wf = pd.read_csv(os.path.join(data_dir, "infosys_workforce_inventory.csv"))
    dm = pd.read_csv(os.path.join(data_dir, "infosys_project_demand.csv"))

    sim = WorkforceSimulator(wf, dm, tax)
    results = sim.run_simulation(upskilling_velocity_pct=30, contractor_surge_hc=30, cross_skilling_mobilization=25, sla_buffer_days=7)
    print("Simulation Output:", results)

