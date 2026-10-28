"""
Workforce Intelligence & Deadline Breach Predictive Analyzer
Project - 06: Workforce Capacity & Skill Gap Problem (Infosys Limited)

Performs:
1. Supply-Demand Mapping & Competency Deficit Identification.
2. Empirical Quantification of the "Paper Capacity Paradox".
3. Critical Skill Gap Criticality Index (CI) calculation.
4. Machine Learning Predictive Classifier for Project Deadline Breaches.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class WorkforceAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.taxonomy_path = os.path.join(data_dir, "infosys_skill_taxonomy.csv")
        self.workforce_path = os.path.join(data_dir, "infosys_workforce_inventory.csv")
        self.demand_path = os.path.join(data_dir, "infosys_project_demand.csv")

        self.df_taxonomy = pd.read_csv(self.taxonomy_path)
        self.df_workforce = pd.read_csv(self.workforce_path)
        self.df_demand = pd.read_csv(self.demand_path)

        self.model = None
        self.scaler = None
        self.feature_names = []
        self.model_metrics = {}
        self.feature_importances = {}

    def get_executive_summary_kpis(self):
        """Calculates global enterprise KPIs highlighting the Paper Capacity Paradox."""
        total_hc = len(self.df_workforce)
        bench_df = self.df_workforce[self.df_workforce["allocation_status"] == "Active_Bench"]
        gross_bench_hc = len(bench_df)
        gross_bench_pct = round((gross_bench_hc / total_hc) * 100, 2)

        # Legacy bench vs Modern bench
        legacy_bench = len(bench_df[bench_df["skill_cluster"] == "Legacy Systems & Support"])
        modern_clusters = ["Generative AI & ML", "Cloud Native & DevOps", "Modern Data & Analytics"]
        modern_bench = len(bench_df[bench_df["skill_cluster"].isin(modern_clusters)])

        # Usable modern bench rate (competency >= 3 in high demand skills)
        usable_modern_bench = len(bench_df[
            (bench_df["skill_cluster"].isin(modern_clusters)) & 
            (bench_df["proficiency_level"] >= 3)
        ])

        # Project demand metrics
        total_projects = len(self.df_demand)
        breached_projects = int(self.df_demand["deadline_breached"].sum())
        breach_rate_pct = round((breached_projects / total_projects) * 100, 2)
        total_penalties_cr = round(float(self.df_demand["sla_penalty_incurred_lakhs"].sum() / 100.0), 2)
        total_contract_value_cr = round(float(self.df_demand["contract_value_cr"].sum()), 2)
        total_unfulfilled_hc = int(self.df_demand["unfulfilled_headcount"].sum())

        return {
            "organization": "Infosys Limited",
            "total_workforce_headcount": total_hc,
            "gross_bench_headcount": gross_bench_hc,
            "gross_bench_rate_pct": gross_bench_pct,
            "legacy_bench_headcount": legacy_bench,
            "legacy_bench_share_pct": round((legacy_bench / max(1, gross_bench_hc)) * 100, 1),
            "modern_bench_headcount": modern_bench,
            "usable_modern_bench_headcount": usable_modern_bench,
            "total_client_projects": total_projects,
            "projects_breached_count": breached_projects,
            "deadline_breach_rate_pct": breach_rate_pct,
            "total_sla_penalties_cr": total_penalties_cr,
            "total_contract_value_cr": total_contract_value_cr,
            "total_unfulfilled_headcount": total_unfulfilled_hc,
        }

    def compute_cluster_level_paradox(self):
        """Quantifies the Paper Capacity Paradox across the 7 technology clusters."""
        clusters = self.df_taxonomy["cluster"].unique()
        records = []

        total_bench = len(self.df_workforce[self.df_workforce["allocation_status"] == "Active_Bench"])

        for cluster in clusters:
            # Supply side
            emp_cluster = self.df_workforce[self.df_workforce["skill_cluster"] == cluster]
            cluster_total_hc = len(emp_cluster)
            cluster_bench = emp_cluster[emp_cluster["allocation_status"] == "Active_Bench"]
            cluster_bench_hc = len(cluster_bench)
            qualified_bench_hc = len(cluster_bench[cluster_bench["proficiency_level"] >= 3])
            
            # Demand side
            demand_cluster = self.df_demand[self.df_demand["skill_cluster"] == cluster]
            demand_hc = int(demand_cluster["required_headcount"].sum())
            unfulfilled_hc = int(demand_cluster["unfulfilled_headcount"].sum())
            breached_prjs = int(demand_cluster["deadline_breached"].sum())
            penalties_cr = round(float(demand_cluster["sla_penalty_incurred_lakhs"].sum() / 100.0), 2)

            # Net Balance = Qualified Bench - Unfulfilled Demand
            net_gap = qualified_bench_hc - unfulfilled_hc
            
            # Paper Paradox Ratio: (Cluster Bench / Total Bench) vs (Cluster Demand / Total Demand)
            records.append({
                "cluster": cluster,
                "total_workforce": cluster_total_hc,
                "bench_headcount": cluster_bench_hc,
                "qualified_bench_headcount": qualified_bench_hc,
                "demand_headcount": demand_hc,
                "unfulfilled_demand": unfulfilled_hc,
                "net_gap": net_gap,
                "status": "Severe Deficit" if net_gap < -25 else "Moderate Deficit" if net_gap < 0 else "Balanced / Surplus",
                "breached_projects": breached_prjs,
                "sla_penalties_cr": penalties_cr
            })

        df_paradox = pd.DataFrame(records).sort_values("net_gap", ascending=True)
        return df_paradox

    def compute_skill_level_gaps(self):
        """Computes granular supply vs demand balance and Criticality Index per skill."""
        skills = self.df_taxonomy["skill_name"].unique()
        records = []

        for skill in skills:
            tax_row = self.df_taxonomy[self.df_taxonomy["skill_name"] == skill].iloc[0]
            cluster = tax_row["cluster"]
            scarcity = tax_row["scarcity"]
            bridge_from = tax_row["bridge_from"]
            bridge_days = tax_row["bridge_days"]

            # Supply: Active Bench with proficiency >= 3
            bench_matches = self.df_workforce[
                (self.df_workforce["primary_skill"] == skill) & 
                (self.df_workforce["allocation_status"] == "Active_Bench")
            ]
            bench_total = len(bench_matches)
            bench_qualified = len(bench_matches[bench_matches["proficiency_level"] >= 3])

            # Rolling release pool (available within 30 days)
            rolling_matches = self.df_workforce[
                (self.df_workforce["primary_skill"] == skill) & 
                (self.df_workforce["allocation_status"] == "Billed_Project") & 
                (self.df_workforce["rolling_release_days"] <= 30) & 
                (self.df_workforce["proficiency_level"] >= 3)
            ]
            rolling_qualified = len(rolling_matches)

            # Demand
            demand_rows = self.df_demand[self.df_demand["required_skill"] == skill]
            demand_count = len(demand_rows)
            demand_hc = int(demand_rows["required_headcount"].sum()) if demand_count > 0 else 0
            unfulfilled_hc = int(demand_rows["unfulfilled_headcount"].sum()) if demand_count > 0 else 0
            penalties_cr = round(float(demand_rows["sla_penalty_incurred_lakhs"].sum() / 100.0), 2) if demand_count > 0 else 0.0

            total_usable_supply = bench_qualified + rolling_qualified
            net_gap = total_usable_supply - unfulfilled_hc

            # Criticality Index (CI): Scarcity * (Deficit if negative) * Revenue at Risk weight
            deficit = max(0, -net_gap)
            criticality_index = round(float(deficit * scarcity * (1.0 + penalties_cr)), 2)

            records.append({
                "skill_name": skill,
                "cluster": cluster,
                "scarcity": scarcity,
                "bench_qualified": bench_qualified,
                "rolling_qualified_30d": rolling_qualified,
                "total_usable_supply": total_usable_supply,
                "project_demand_hc": demand_hc,
                "unfulfilled_hc": unfulfilled_hc,
                "net_gap": net_gap,
                "criticality_index": criticality_index,
                "sla_penalties_cr": penalties_cr,
                "bridge_from": bridge_from,
                "bridge_days": bridge_days
            })

        df_gaps = pd.DataFrame(records).sort_values("criticality_index", ascending=False)
        return df_gaps

    def train_deadline_predictor(self):
        """Trains machine learning models to predict project deadline breach probability."""
        df = self.df_demand.copy()

        # Feature Engineering
        df["unfulfilled_ratio"] = df["unfulfilled_headcount"] / df["required_headcount"].clip(lower=1)
        df["lead_urgency"] = 1.0 / df["staffing_deadline_days"].clip(lower=7)
        df["penalty_exposure"] = df["sla_penalty_per_week_lakhs"] * (df["unfulfilled_headcount"] / df["required_headcount"].clip(lower=1))

        # Categorical encoding
        df["is_tier1"] = (df["priority_tier"] == "Tier-1 Strategic").astype(int)
        
        feature_cols = [
            "required_headcount",
            "unfulfilled_headcount",
            "unfulfilled_ratio",
            "staffing_deadline_days",
            "lead_urgency",
            "contract_value_cr",
            "sla_penalty_per_week_lakhs",
            "penalty_exposure",
            "required_min_proficiency",
            "skill_scarcity_index",
            "is_tier1"
        ]

        X = df[feature_cols]
        y = df["deadline_breached"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Gradient Boosting Classifier
        clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]

        self.model = clf
        self.feature_names = feature_cols
        self.model_metrics = {
            "model_name": "Gradient Boosting Classifier",
            "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred)), 4),
            "recall": round(float(recall_score(y_test, y_pred)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred)), 4)
        }

        # Feature Importances
        importances = clf.feature_importances_
        feat_imp = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        self.feature_importances = {k: round(float(v), 4) for k, v in feat_imp}

        return self.model_metrics

    def predict_project_risk(self, project_data: dict):
        """Predicts deadline breach probability for a given project specification."""
        if self.model is None:
            self.train_deadline_predictor()

        req_hc = project_data.get("required_headcount", 8)
        unf_hc = project_data.get("unfulfilled_headcount", 3)
        unf_ratio = unf_hc / max(1, req_hc)
        deadline_days = project_data.get("staffing_deadline_days", 21)
        lead_urgency = 1.0 / max(7, deadline_days)
        contract_cr = project_data.get("contract_value_cr", 15.0)
        penalty_pw = project_data.get("sla_penalty_per_week_lakhs", 12.0)
        pen_exp = penalty_pw * unf_ratio
        min_prof = project_data.get("required_min_proficiency", 4)
        scarcity = project_data.get("skill_scarcity_index", 0.90)
        is_tier1 = 1 if "Tier-1" in project_data.get("priority_tier", "") else 0

        features = pd.DataFrame([{
            "required_headcount": req_hc,
            "unfulfilled_headcount": unf_hc,
            "unfulfilled_ratio": unf_ratio,
            "staffing_deadline_days": deadline_days,
            "lead_urgency": lead_urgency,
            "contract_value_cr": contract_cr,
            "sla_penalty_per_week_lakhs": penalty_pw,
            "penalty_exposure": pen_exp,
            "required_min_proficiency": min_prof,
            "skill_scarcity_index": scarcity,
            "is_tier1": is_tier1
        }])[self.feature_names]

        prob = float(self.model.predict_proba(features)[0][1])
        prediction = int(prob >= 0.50)

        risk_category = "CRITICAL BREACH IMMINENT" if prob >= 0.75 else "ELEVATED RISK" if prob >= 0.50 else "MODERATE / MONITOR" if prob >= 0.25 else "LOW / ON TRACK"

        return {
            "breach_probability": round(prob, 4),
            "predicted_breach": prediction,
            "risk_category": risk_category
        }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    analyzer = WorkforceAnalyzer(data_dir)
    kpis = analyzer.get_executive_summary_kpis()
    print("Executive KPIs:", kpis)
    metrics = analyzer.train_deadline_predictor()
    print("Model Metrics:", metrics)
    print("Top Feature Drivers:", analyzer.feature_importances)
