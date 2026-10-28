"""
Dataset Generator for Project - 06: Workforce Capacity & Skill Gap Problem
Infosys Limited - Workforce Intelligence & Strategic Capacity Allocation System

Generates multi-dimensional enterprise datasets:
1. infosys_skill_taxonomy.csv: Standardized competency hierarchy across 7 technology clusters.
2. infosys_workforce_inventory.csv: 14,000 employee records with validated skills, proficiencies, JL bands, and bench telemetry.
3. infosys_project_demand.csv: 220 enterprise transformation engagements with skill requirements, kickoff SLAs, and penalty telemetry.
"""

import os
import sys
import json
import random
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Set reproducible random seed
np.random.seed(42)
random.seed(42)

# Technology Clusters & Skill Taxonomy Definition
SKILL_TAXONOMY = [
    # Cluster 1: Generative AI & Advanced Machine Learning
    {"skill_id": "SK-AI-01", "skill_name": "GenAI & LLM Fine-Tuning", "cluster": "Generative AI & ML", "scarcity": 0.94, "market_rate_usd": 125, "bridge_from": "Python / Core ML", "bridge_days": 28, "difficulty": "High"},
    {"skill_id": "SK-AI-02", "skill_name": "Prompt Engineering & RAG Systems", "cluster": "Generative AI & ML", "scarcity": 0.88, "market_rate_usd": 110, "bridge_from": "Python / NLP Basics", "bridge_days": 21, "difficulty": "Medium"},
    {"skill_id": "SK-AI-03", "skill_name": "MLOps & Model Governance", "cluster": "Generative AI & ML", "scarcity": 0.91, "market_rate_usd": 120, "bridge_from": "DevOps & Docker", "bridge_days": 30, "difficulty": "High"},
    {"skill_id": "SK-AI-04", "skill_name": "Computer Vision & Deep Learning", "cluster": "Generative AI & ML", "scarcity": 0.82, "market_rate_usd": 115, "bridge_from": "Data Science / Python", "bridge_days": 35, "difficulty": "High"},

    # Cluster 2: Cloud Native & Distributed Systems
    {"skill_id": "SK-CL-01", "skill_name": "Kubernetes & Microservices (EKS/GKE)", "cluster": "Cloud Native & DevOps", "scarcity": 0.89, "market_rate_usd": 115, "bridge_from": "Docker / Linux Admin", "bridge_days": 25, "difficulty": "Medium"},
    {"skill_id": "SK-CL-02", "skill_name": "AWS/Azure Cloud Solutions Architecture", "cluster": "Cloud Native & DevOps", "scarcity": 0.86, "market_rate_usd": 130, "bridge_from": "Infrastructure Admin", "bridge_days": 35, "difficulty": "High"},
    {"skill_id": "SK-CL-03", "skill_name": "Golang High-Concurrency Systems", "cluster": "Cloud Native & DevOps", "scarcity": 0.85, "market_rate_usd": 118, "bridge_from": "C++ / Java Backend", "bridge_days": 24, "difficulty": "Medium"},
    {"skill_id": "SK-CL-04", "skill_name": "Terraform & Multi-Cloud CI/CD", "cluster": "Cloud Native & DevOps", "scarcity": 0.79, "market_rate_usd": 105, "bridge_from": "Jenkins / Scripting", "bridge_days": 18, "difficulty": "Low"},

    # Cluster 3: Modern Data Engineering & Analytics
    {"skill_id": "SK-DT-01", "skill_name": "Databricks & PySpark Lakehouse", "cluster": "Modern Data & Analytics", "scarcity": 0.92, "market_rate_usd": 122, "bridge_from": "SQL / Python ETL", "bridge_days": 21, "difficulty": "Medium"},
    {"skill_id": "SK-DT-02", "skill_name": "Snowflake Cloud Data Warehousing", "cluster": "Modern Data & Analytics", "scarcity": 0.84, "market_rate_usd": 112, "bridge_from": "Oracle / SQL Server", "bridge_days": 18, "difficulty": "Low"},
    {"skill_id": "SK-DT-03", "skill_name": "Apache Kafka Real-Time Streaming", "cluster": "Modern Data & Analytics", "scarcity": 0.87, "market_rate_usd": 115, "bridge_from": "Java / Messaging Queues", "bridge_days": 22, "difficulty": "Medium"},
    {"skill_id": "SK-DT-04", "skill_name": "dbt & Modern Analytics Engineering", "cluster": "Modern Data & Analytics", "scarcity": 0.76, "market_rate_usd": 98, "bridge_from": "SQL / BI Reporting", "bridge_days": 14, "difficulty": "Low"},

    # Cluster 4: Modern Full-Stack & Mobile
    {"skill_id": "SK-FS-01", "skill_name": "React / Next.js & TypeScript", "cluster": "Modern Full-Stack & UI", "scarcity": 0.78, "market_rate_usd": 95, "bridge_from": "Angular / JavaScript", "bridge_days": 16, "difficulty": "Low"},
    {"skill_id": "SK-FS-02", "skill_name": "Java Spring Boot & Reactive Microservices", "cluster": "Modern Full-Stack & UI", "scarcity": 0.74, "market_rate_usd": 95, "bridge_from": "Core Java / J2EE", "bridge_days": 20, "difficulty": "Medium"},
    {"skill_id": "SK-FS-03", "skill_name": "Flutter / React Native Cross-Platform", "cluster": "Modern Full-Stack & UI", "scarcity": 0.75, "market_rate_usd": 92, "bridge_from": "Native Android / iOS", "bridge_days": 18, "difficulty": "Low"},

    # Cluster 5: Enterprise Applications & SaaS
    {"skill_id": "SK-EP-01", "skill_name": "SAP S/4HANA Cloud Migration & FICO", "cluster": "Enterprise ERP & SaaS", "scarcity": 0.93, "market_rate_usd": 135, "bridge_from": "SAP ECC 6.0", "bridge_days": 40, "difficulty": "High"},
    {"skill_id": "SK-EP-02", "skill_name": "Salesforce Financial Services Cloud (FSC)", "cluster": "Enterprise ERP & SaaS", "scarcity": 0.83, "market_rate_usd": 110, "bridge_from": "Salesforce Classic Admin", "bridge_days": 24, "difficulty": "Medium"},
    {"skill_id": "SK-EP-03", "skill_name": "ServiceNow ITOM & SecOps", "cluster": "Enterprise ERP & SaaS", "scarcity": 0.81, "market_rate_usd": 105, "bridge_from": "ITIL / Helpdesk Support", "bridge_days": 21, "difficulty": "Medium"},

    # Cluster 6: Cybersecurity & Zero Trust
    {"skill_id": "SK-CY-01", "skill_name": "Zero Trust Architecture & IAM (Okta/Ping)", "cluster": "Cyber Defense & SecOps", "scarcity": 0.89, "market_rate_usd": 125, "bridge_from": "Active Directory / Network", "bridge_days": 28, "difficulty": "High"},
    {"skill_id": "SK-CY-02", "skill_name": "Cloud Security Posture Management (CSPM)", "cluster": "Cyber Defense & SecOps", "scarcity": 0.86, "market_rate_usd": 118, "bridge_from": "SysAdmin / Linux", "bridge_days": 22, "difficulty": "Medium"},

    # Cluster 7: Legacy & Maintenance Pools (High bench surplus, low demand)
    {"skill_id": "SK-LG-01", "skill_name": "Legacy Mainframe (COBOL / JCL / CICS)", "cluster": "Legacy Systems & Support", "scarcity": 0.25, "market_rate_usd": 65, "bridge_from": "None", "bridge_days": 45, "difficulty": "High"},
    {"skill_id": "SK-LG-02", "skill_name": "Manual Regression Testing & QA", "cluster": "Legacy Systems & Support", "scarcity": 0.20, "market_rate_usd": 45, "bridge_from": "None", "bridge_days": 14, "difficulty": "Low"},
    {"skill_id": "SK-LG-03", "skill_name": "Monolithic Java 7/8 Maintenance", "cluster": "Legacy Systems & Support", "scarcity": 0.30, "market_rate_usd": 60, "bridge_from": "None", "bridge_days": 20, "difficulty": "Medium"},
    {"skill_id": "SK-LG-04", "skill_name": "On-Prem Oracle / PL-SQL DBA", "cluster": "Legacy Systems & Support", "scarcity": 0.35, "market_rate_usd": 68, "bridge_from": "None", "bridge_days": 22, "difficulty": "Medium"},
    {"skill_id": "SK-LG-05", "skill_name": "L1/L2 Application Support & Ticketing", "cluster": "Legacy Systems & Support", "scarcity": 0.18, "market_rate_usd": 40, "bridge_from": "None", "bridge_days": 18, "difficulty": "Low"},
]

DELIVERY_UNITS = [
    ("FS", "Financial Services & Insurance", 0.32),
    ("MFG", "Manufacturing & Hi-Tech", 0.22),
    ("RCL", "Retail, CPG & Logistics", 0.20),
    ("ECS", "Energy, Utilities & Services", 0.14),
    ("HLS", "Healthcare & Life Sciences", 0.12),
]

LOCATIONS = [
    ("Bengaluru (Electronic City)", 0.38),
    ("Pune (Hinjawadi)", 0.22),
    ("Hyderabad (Gachibowli)", 0.18),
    ("Chennai (Sholinganallur)", 0.10),
    ("Mysuru Campus", 0.05),
    ("Dallas / Plano (US Hub)", 0.04),
    ("Frankfurt (EU Hub)", 0.03),
]

JOB_LEVELS = [
    ("JL3", "Systems Engineer", 1, 3, 0.30, 42000, 65000),
    ("JL4", "Senior Systems Engineer", 3, 6, 0.35, 70000, 115000),
    ("JL5", "Technology Lead / Specialist", 6, 10, 0.22, 125000, 195000),
    ("JL6", "Technology Architect / PM", 10, 15, 0.10, 210000, 310000),
    ("JL7", "Principal Consultant / Director", 15, 23, 0.03, 330000, 480000),
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Ananya", "Arjun", "Deepak", "Divya", "Gaurav", "Harsh", "Ishaan", "Kavya",
    "Manish", "Meera", "Neha", "Nikhil", "Pooja", "Pranav", "Priya", "Rahul", "Rakesh", "Riya",
    "Rohan", "Sanjay", "Shreya", "Siddharth", "Sneha", "Sunil", "Tanvi", "Varun", "Vikas", "Zoya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Rao", "Kulkarni", "Mehta", "Chatterjee",
    "Singh", "Bose", "Gupta", "Deshmukh", "Nambiar", "Pillai", "Joshi", "Bhat", "Chopra", "Das"
]

def generate_workforce_dataset(output_dir: str, n_employees: int = 14000, n_projects: int = 220):
    """Generates the three interrelated Infosys workforce, demand, and skill taxonomy datasets."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Skill Taxonomy Dataframe
    df_skills = pd.DataFrame(SKILL_TAXONOMY)
    taxonomy_path = os.path.join(output_dir, "infosys_skill_taxonomy.csv")
    df_skills.to_csv(taxonomy_path, index=False)
    print(f"  [OK] Created Skill Taxonomy ({len(df_skills)} skills across 7 clusters) -> {taxonomy_path}")

    # Skill probability weights for supply (The "Paper Capacity Paradox"):
    skill_weights_supply = []
    for s in SKILL_TAXONOMY:
        if s["cluster"] == "Legacy Systems & Support":
            skill_weights_supply.append(0.38 / 5)  # 38% of total talent in legacy maintenance!
        elif s["cluster"] == "Modern Full-Stack & UI":
            skill_weights_supply.append(0.20 / 3)
        elif s["cluster"] == "Cloud Native & DevOps":
            skill_weights_supply.append(0.14 / 4)
        elif s["cluster"] == "Modern Data & Analytics":
            skill_weights_supply.append(0.11 / 4)
        elif s["cluster"] == "Enterprise ERP & SaaS":
            skill_weights_supply.append(0.08 / 3)
        elif s["cluster"] == "Cyber Defense & SecOps":
            skill_weights_supply.append(0.04 / 2)
        elif s["cluster"] == "Generative AI & ML":
            skill_weights_supply.append(0.05 / 4)  # Only 5% of total supply in GenAI/ML!
    skill_weights_supply = np.array(skill_weights_supply)
    skill_weights_supply = skill_weights_supply / skill_weights_supply.sum()

    # 2. Employee Workforce Telemetry (14,000 Employees)
    du_names = [d[0] for d in DELIVERY_UNITS]
    du_weights = [d[2] for d in DELIVERY_UNITS]
    
    loc_names = [l[0] for l in LOCATIONS]
    loc_weights = [l[1] for l in LOCATIONS]
    
    jl_levels = [j[0] for j in JOB_LEVELS]
    jl_weights = [j[4] for j in JOB_LEVELS]
    
    emp_records = []
    for i in range(1, n_employees + 1):
        emp_id = f"INF-{100000 + i}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        du = np.random.choice(du_names, p=du_weights)
        location = np.random.choice(loc_names, p=loc_weights)
        
        jl_idx = np.random.choice(len(jl_levels), p=jl_weights)
        jl_info = JOB_LEVELS[jl_idx]
        jl = jl_info[0]
        exp_years = round(np.random.uniform(jl_info[2], jl_info[3]), 1)
        monthly_ctc = int(np.random.uniform(jl_info[5], jl_info[6]))
        
        skill_obj = np.random.choice(SKILL_TAXONOMY, p=skill_weights_supply)
        primary_skill = skill_obj["skill_name"]
        cluster = skill_obj["cluster"]
        
        if skill_obj["cluster"] == "Legacy Systems & Support":
            proficiency = np.random.choice([2, 3, 4, 5], p=[0.10, 0.40, 0.35, 0.15])
            status = np.random.choice(["Active_Bench", "Billed_Project", "Lex_Academy_Training"], p=[0.28, 0.65, 0.07])
        elif skill_obj["cluster"] in ["Generative AI & ML", "Modern Data & Analytics"]:
            proficiency = np.random.choice([1, 2, 3, 4, 5], p=[0.25, 0.35, 0.25, 0.12, 0.03])
            status = np.random.choice(["Active_Bench", "Billed_Project", "Shadow_RampUp"], p=[0.04, 0.90, 0.06])
        else:
            proficiency = np.random.choice([1, 2, 3, 4, 5], p=[0.12, 0.28, 0.38, 0.17, 0.05])
            status = np.random.choice(["Active_Bench", "Billed_Project", "Shadow_RampUp", "Lex_Academy_Training"], p=[0.12, 0.78, 0.06, 0.04])
            
        if status == "Active_Bench":
            rolling_release_days = 0
            bench_days = int(np.random.exponential(scale=45)) + 5
            bench_days = min(bench_days, 210)
        elif status == "Billed_Project":
            bench_days = 0
            rolling_release_days = int(np.random.choice([14, 30, 45, 60, 90, 120, 180], p=[0.10, 0.15, 0.20, 0.25, 0.15, 0.10, 0.05]))
        elif status == "Shadow_RampUp":
            bench_days = 0
            rolling_release_days = int(np.random.choice([7, 14, 21], p=[0.3, 0.5, 0.2]))
        else:
            bench_days = 0
            rolling_release_days = int(np.random.choice([14, 21, 28, 35], p=[0.2, 0.4, 0.3, 0.1]))

        secondary_choices = [s["skill_name"] for s in SKILL_TAXONOMY if s["skill_name"] != primary_skill]
        secondary_skill = random.choice(secondary_choices)
        
        has_certification = 1 if np.random.rand() < (0.35 + 0.1 * proficiency) else 0
        productivity_rating = round(float(np.clip(np.random.normal(82, 8), 60, 99)), 1)
        relocation_ready = 1 if np.random.rand() < 0.72 else 0

        emp_records.append({
            "employee_id": emp_id,
            "full_name": name,
            "delivery_unit": du,
            "base_location": location,
            "job_level": jl,
            "experience_years": exp_years,
            "primary_skill": primary_skill,
            "skill_cluster": cluster,
            "proficiency_level": proficiency,
            "secondary_skill": secondary_skill,
            "has_certification": has_certification,
            "allocation_status": status,
            "rolling_release_days": rolling_release_days,
            "bench_duration_days": bench_days,
            "monthly_ctc_inr": monthly_ctc,
            "productivity_rating": productivity_rating,
            "relocation_ready": relocation_ready
        })

    df_workforce = pd.DataFrame(emp_records)
    workforce_path = os.path.join(output_dir, "infosys_workforce_inventory.csv")
    df_workforce.to_csv(workforce_path, index=False)
    
    total_bench = (df_workforce["allocation_status"] == "Active_Bench").sum()
    bench_rate = (total_bench / len(df_workforce)) * 100
    print(f"  [OK] Created Workforce Inventory ({len(df_workforce):,} employees) -> {workforce_path}")
    print(f"    • Total Active Bench: {total_bench:,} ({bench_rate:.1f}% on paper)")

    # 3. Enterprise Project Demand Pipeline (220 Projects)
    skill_weights_demand = []
    for s in SKILL_TAXONOMY:
        if s["cluster"] == "Generative AI & ML":
            skill_weights_demand.append(0.24 / 4)
        elif s["cluster"] == "Cloud Native & DevOps":
            skill_weights_demand.append(0.22 / 4)
        elif s["cluster"] == "Modern Data & Analytics":
            skill_weights_demand.append(0.22 / 4)
        elif s["cluster"] == "Enterprise ERP & SaaS":
            skill_weights_demand.append(0.14 / 3)
        elif s["cluster"] == "Modern Full-Stack & UI":
            skill_weights_demand.append(0.12 / 3)
        elif s["cluster"] == "Cyber Defense & SecOps":
            skill_weights_demand.append(0.05 / 2)
        elif s["cluster"] == "Legacy Systems & Support":
            skill_weights_demand.append(0.01 / 5)
    skill_weights_demand = np.array(skill_weights_demand)
    skill_weights_demand = skill_weights_demand / skill_weights_demand.sum()

    CLIENT_PROFILES = [
        ("JPMorgan Chase & Co.", "FS"), ("Bank of America", "FS"), ("HSBC Holdings", "FS"), ("Wells Fargo", "FS"),
        ("Walmart Global Tech", "RCL"), ("Target Corporation", "RCL"), ("Procter & Gamble", "RCL"), ("Unilever", "RCL"),
        ("BMW Group Digital", "MFG"), ("Boeing Commercial", "MFG"), ("Siemens AG", "MFG"), ("Caterpillar Inc.", "MFG"),
        ("BP International", "ECS"), ("Chevron Digital", "ECS"), ("NextEra Energy", "ECS"), ("Vodafone Group", "ECS"),
        ("Pfizer Biopharma", "HLS"), ("Johnson & Johnson", "HLS"), ("Novartis Pharma", "HLS"), ("AstraZeneca", "HLS"),
    ]

    PROJECT_TEMPLATES = [
        ("GenAI Copilot for Regulatory Risk & Trade Compliance", "Generative AI & ML", 4),
        ("Autonomous Financial Fraud Detection & Graph LLM Engine", "Generative AI & ML", 4),
        ("Omnichannel Customer RAG Intelligence Platform", "Generative AI & ML", 3),
        ("Enterprise MLOps Model Monitoring & LLM Guardrails", "Generative AI & ML", 4),
        ("Multi-Cloud Hybrid Kubernetes (EKS) Transformation", "Cloud Native & DevOps", 4),
        ("Microservices Architecture Re-platforming for Core Banking", "Cloud Native & DevOps", 3),
        ("High-Frequency Order Matching Engine in Golang", "Cloud Native & DevOps", 4),
        ("Enterprise Multi-Region Terraform CI/CD Automation", "Cloud Native & DevOps", 3),
        ("Enterprise Databricks Lakehouse & Real-time Telemetry", "Modern Data & Analytics", 4),
        ("Global Snowflake Modern Data Warehouse Consolidation", "Modern Data & Analytics", 3),
        ("Low-Latency Apache Kafka Event Streaming Grid", "Modern Data & Analytics", 4),
        ("Modern dbt Semantic Layer & Enterprise BI Modernization", "Modern Data & Analytics", 3),
        ("Next-Gen Digital Banking Portal (React 19 & TypeScript)", "Modern Full-Stack & UI", 3),
        ("Reactive Spring Boot 3 Microservices Platform", "Modern Full-Stack & UI", 3),
        ("Global Mobile Retail App (Flutter Cross-Platform)", "Modern Full-Stack & UI", 3),
        ("SAP S/4HANA Finance & Supply Chain Cloud Migration", "Enterprise ERP & SaaS", 4),
        ("Salesforce Financial Services Cloud CRM Overhaul", "Enterprise ERP & SaaS", 3),
        ("ServiceNow Enterprise SecOps & ITOM Automation", "Enterprise ERP & SaaS", 3),
        ("Zero-Trust Identity Governance & Cloud Security (CSPM)", "Cyber Defense & SecOps", 4),
        ("Mainframe Offloading & Cloud Data Sync Service", "Legacy Systems & Support", 3),
    ]

    project_records = []
    for p_idx in range(1, n_projects + 1):
        prj_id = f"PRJ-{1000 + p_idx}"
        client_name, default_du = random.choice(CLIENT_PROFILES)
        
        req_skill_obj = np.random.choice(SKILL_TAXONOMY, p=skill_weights_demand)
        req_skill = req_skill_obj["skill_name"]
        req_cluster = req_skill_obj["cluster"]
        scarcity = req_skill_obj["scarcity"]
        
        matching_tmpls = [t for t in PROJECT_TEMPLATES if t[1] == req_cluster]
        if matching_tmpls:
            base_title, _, min_prof_default = random.choice(matching_tmpls)
            prj_name = f"{client_name.split()[0]} - {base_title}"
            min_proficiency = min_prof_default
        else:
            prj_name = f"{client_name.split()[0]} - {req_skill} Modernization"
            min_proficiency = 3

        required_hc = int(np.random.choice([4, 6, 8, 12, 16, 22, 30], p=[0.20, 0.25, 0.22, 0.15, 0.10, 0.05, 0.03]))
        kickoff_lead_days = int(np.random.choice([7, 14, 21, 30, 45, 60], p=[0.12, 0.25, 0.28, 0.18, 0.12, 0.05]))
        contract_value_cr = round(float(np.random.uniform(4.0, 38.0)), 2)
        penalty_per_week_lakhs = round(float(contract_value_cr * np.random.uniform(0.6, 1.4)), 2)
        priority_tier = np.random.choice(["Tier-1 Strategic", "Tier-2 Enterprise", "Tier-3 Standard"], p=[0.25, 0.50, 0.25])
        
        is_high_scarcity = (scarcity >= 0.85)
        is_tight_deadline = (kickoff_lead_days <= 21)
        
        if is_high_scarcity and is_tight_deadline:
            fill_pct = np.random.uniform(0.45, 0.75)
        elif is_high_scarcity or is_tight_deadline:
            fill_pct = np.random.uniform(0.70, 0.90)
        else:
            fill_pct = np.random.uniform(0.88, 1.0)
            
        allocated_hc = int(round(required_hc * fill_pct))
        allocated_hc = max(1, min(allocated_hc, required_hc))
        unfulfilled_hc = required_hc - allocated_hc
        
        if unfulfilled_hc == 0:
            deadline_breached = 0
        else:
            unfulfilled_ratio = unfulfilled_hc / required_hc
            breach_prob = (unfulfilled_ratio * 0.50) + (scarcity * 0.35) + (0.25 if kickoff_lead_days <= 14 else 0.10 if kickoff_lead_days <= 28 else 0.0)
            deadline_breached = 1 if (breach_prob > 0.65 or (unfulfilled_ratio >= 0.30 and kickoff_lead_days <= 21)) else 0
        
        if deadline_breached:
            delay_days = int(np.random.choice([14, 21, 28, 35, 49, 63], p=[0.20, 0.30, 0.25, 0.15, 0.06, 0.04]))
            sla_penalty_incurred_lakhs = round(float((delay_days / 7.0) * penalty_per_week_lakhs), 2)
        else:
            delay_days = 0
            sla_penalty_incurred_lakhs = 0.0

        project_records.append({
            "project_id": prj_id,
            "project_name": prj_name,
            "client_name": client_name,
            "delivery_unit": default_du,
            "target_location": random.choice(loc_names),
            "required_skill": req_skill,
            "skill_cluster": req_cluster,
            "required_min_proficiency": min_proficiency,
            "required_headcount": required_hc,
            "allocated_headcount": allocated_hc,
            "unfulfilled_headcount": unfulfilled_hc,
            "staffing_deadline_days": kickoff_lead_days,
            "contract_value_cr": contract_value_cr,
            "sla_penalty_per_week_lakhs": penalty_per_week_lakhs,
            "priority_tier": priority_tier,
            "deadline_breached": deadline_breached,
            "actual_delay_days": delay_days,
            "sla_penalty_incurred_lakhs": sla_penalty_incurred_lakhs,
            "skill_scarcity_index": scarcity
        })

    df_projects = pd.DataFrame(project_records)
    projects_path = os.path.join(output_dir, "infosys_project_demand.csv")
    df_projects.to_csv(projects_path, index=False)

    breach_count = df_projects["deadline_breached"].sum()
    breach_pct = (breach_count / len(df_projects)) * 100
    total_penalty_cr = df_projects["sla_penalty_incurred_lakhs"].sum() / 100.0
    print(f"  [OK] Created Project Demand Pipeline ({len(df_projects)} client projects) -> {projects_path}")
    print(f"    • Projects Breaching Deadlines: {breach_count}/{len(df_projects)} ({breach_pct:.1f}%)")
    print(f"    • Total SLA Delay Penalties Incurred: ₹{total_penalty_cr:.2f} Crores")

    return df_skills, df_workforce, df_projects

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    generate_workforce_dataset(current_dir)

