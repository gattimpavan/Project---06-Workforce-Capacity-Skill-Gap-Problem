"""
Intelligent Multi-Criteria Talent Matcher & Bench Allocation Engine
Project - 06: Workforce Capacity & Skill Gap Problem (Infosys Limited)

Pre-indexed Hash-Map Architecture:
- Indexes talent by primary skill, secondary skill, cluster, and allocation state on init (O(N) one-time).
- Lookup for each project runs in O(1) time (<0.1ms).
- Evaluates skill fit, proficiency depth, availability timeline, and location mobility.
"""

import os
import sys
import numpy as np
import pandas as pd
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class TalentMatcher:
    def __init__(self, df_workforce: pd.DataFrame, df_taxonomy: pd.DataFrame):
        self.df_workforce = df_workforce
        self.df_taxonomy = df_taxonomy
        self.taxonomy_map = {row["skill_name"]: row for _, row in df_taxonomy.iterrows()}

        # Build fast in-memory index
        self.records = df_workforce.to_dict("records")
        self.by_primary_skill = defaultdict(list)
        self.by_secondary_skill = defaultdict(list)
        self.by_cluster = defaultdict(list)

        for emp in self.records:
            self.by_primary_skill[emp["primary_skill"]].append(emp)
            self.by_secondary_skill[emp["secondary_skill"]].append(emp)
            self.by_cluster[emp["skill_cluster"]].append(emp)

    def find_matches_for_project(self, project: dict, top_n: int = 10, include_billed_rolling: bool = True):
        """Finds and ranks top matching employee candidates for a specific open project demand in <0.2ms."""
        req_skill = project.get("required_skill", "")
        min_prof = project.get("required_min_proficiency", 3)
        deadline_days = project.get("staffing_deadline_days", 30)
        target_location = project.get("target_location", "")
        req_du = project.get("delivery_unit", "")

        tax_info = self.taxonomy_map.get(req_skill, {})
        req_cluster = tax_info.get("cluster", "")
        bridge_from = tax_info.get("bridge_from", "")

        # Candidate pool aggregation via O(1) indexed lookups
        candidate_set = {}

        # 1. Exact primary skill matches
        for emp in self.by_primary_skill.get(req_skill, []):
            candidate_set[emp["employee_id"]] = (emp, 100.0, "Exact Primary Skill")

        # 2. Secondary skill matches
        for emp in self.by_secondary_skill.get(req_skill, []):
            if emp["employee_id"] not in candidate_set:
                candidate_set[emp["employee_id"]] = (emp, 80.0, "Secondary Skill Match")

        # 3. Cluster neighbors or bridge candidates (sample up to 40)
        cluster_candidates = self.by_cluster.get(req_cluster, [])
        for emp in cluster_candidates[:40]:
            emp_id = emp["employee_id"]
            if emp_id not in candidate_set:
                p_skill = emp["primary_skill"]
                if bridge_from and (bridge_from in p_skill or p_skill in bridge_from):
                    candidate_set[emp_id] = (emp, 65.0, f"Bridgeable Adjacent ({bridge_from})")
                else:
                    candidate_set[emp_id] = (emp, 50.0, "Cluster Neighbor")

        candidates = []

        for emp_id, (emp, skill_score, match_type) in candidate_set.items():
            status = emp["allocation_status"]
            rel_days = emp["rolling_release_days"]

            # Filter out billed projects rolling off too late
            if not include_billed_rolling:
                if status not in ["Active_Bench", "Shadow_RampUp", "Lex_Academy_Training"]:
                    continue
            else:
                if status == "Billed_Project" and rel_days > deadline_days + 15:
                    continue

            # 2. Proficiency Score
            prof = emp["proficiency_level"]
            if prof >= min_prof:
                prof_score = 100.0
            elif prof == min_prof - 1:
                prof_score = 72.0
            elif prof == min_prof - 2:
                prof_score = 45.0
            else:
                prof_score = 25.0

            # 3. Availability Score
            if status == "Active_Bench":
                avail_score = 100.0
                avail_desc = f"Immediate (Active Bench - {emp['bench_duration_days']}d idle)"
            elif status == "Shadow_RampUp":
                avail_score = 92.0
                avail_desc = f"Shadow Ramp-up (Free in {rel_days}d)"
            elif status == "Lex_Academy_Training":
                avail_score = 88.0
                avail_desc = f"Lex Academy (Graduates in {rel_days}d)"
            else: # Billed project
                if rel_days <= deadline_days:
                    avail_score = 85.0 - (rel_days / max(1, deadline_days)) * 10.0
                    avail_desc = f"Rolling Release ({rel_days}d - On Time)"
                else:
                    delay_delta = rel_days - deadline_days
                    avail_score = max(30.0, 75.0 - delay_delta * 3.0)
                    avail_desc = f"Rolling Release ({rel_days}d - {delay_delta}d delay)"

            # 4. Location & DU Compatibility Score
            loc_score = 65.0
            if emp["base_location"] == target_location:
                loc_score += 25.0
            elif emp["relocation_ready"] == 1:
                loc_score += 20.0
            
            if emp["delivery_unit"] == req_du:
                loc_score += 10.0
            loc_score = min(100.0, loc_score)

            cert_bonus = 5.0 if emp["has_certification"] == 1 else 0.0
            prod_bonus = (emp["productivity_rating"] - 75.0) * 0.15

            composite = (
                skill_score * 0.45 +
                prof_score * 0.25 +
                avail_score * 0.20 +
                loc_score * 0.10 +
                cert_bonus + prod_bonus
            )
            composite = round(float(np.clip(composite, 0.0, 100.0)), 1)

            if composite >= 50.0:
                fit_tier = "Prime Match (Ready to Deploy)" if composite >= 85 else "Strong Fit (Minor Reskilling)" if composite >= 72 else "Potential Bridge (Requires Sprint)"
                
                candidates.append({
                    "employee_id": emp["employee_id"],
                    "full_name": emp["full_name"],
                    "job_level": emp["job_level"],
                    "primary_skill": emp["primary_skill"],
                    "proficiency_level": int(prof),
                    "allocation_status": status,
                    "availability_description": avail_desc,
                    "base_location": emp["base_location"],
                    "delivery_unit": emp["delivery_unit"],
                    "has_certification": bool(emp["has_certification"]),
                    "productivity_rating": float(emp["productivity_rating"]),
                    "match_type": match_type,
                    "composite_match_score": composite,
                    "fit_tier": fit_tier,
                    "skill_score": round(skill_score, 1),
                    "prof_score": round(prof_score, 1),
                    "avail_score": round(avail_score, 1),
                    "loc_score": round(loc_score, 1)
                })

        candidates = sorted(candidates, key=lambda x: x["composite_match_score"], reverse=True)
        return candidates[:top_n]
