/**
 * Interactive Executive Dashboard JavaScript
 * Project - 06: Workforce Capacity & Skill Gap Problem
 * Infosys Limited - AI Workforce Intelligence & Strategic Capacity Allocation
 */

let charts = {};
let allSkillsData = [];
let allProjectsData = [];

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadDashboardSummary();
    loadClusterParadox();
    loadSkillMatrix();
    loadRecommendations();
    loadProjectDropdown();
    initSimulator();
});

// -------------------------------------------------------------
// Tab Switching System
// -------------------------------------------------------------
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add("active");
            }
        });
    });
}

// -------------------------------------------------------------
// Executive KPI Summary Loading
// -------------------------------------------------------------
async function loadDashboardSummary() {
    try {
        const res = await fetch("/api/summary");
        const json = await res.json();
        if (json.status !== "success") return;
        const kpis = json.data;

        // Populate Top KPI Cards
        document.getElementById("kpi-workforce").textContent = kpis.total_workforce_headcount.toLocaleString();
        document.getElementById("kpi-bench-headcount").textContent = `${kpis.gross_bench_headcount.toLocaleString()} (${kpis.gross_bench_rate_pct}%)`;
        document.getElementById("kpi-legacy-share").textContent = `${kpis.legacy_bench_share_pct}%`;
        document.getElementById("kpi-legacy-desc").textContent = `${kpis.legacy_bench_headcount.toLocaleString()} in COBOL / Manual QA / Java 7`;

        document.getElementById("kpi-breach-rate").textContent = `${kpis.deadline_breach_rate_pct}%`;
        document.getElementById("kpi-breach-desc").textContent = `${kpis.projects_breached_count} of ${kpis.total_client_projects} projects delayed`;

        document.getElementById("kpi-penalties").textContent = `₹${kpis.total_sla_penalties_cr.toFixed(2)} Cr`;
        document.getElementById("kpi-contract-value").textContent = `₹${kpis.total_contract_value_cr.toFixed(1)} Cr total contract value`;

        document.getElementById("kpi-unfulfilled-hc").textContent = `${kpis.total_unfulfilled_headcount} Seats`;
        
        // Model stats
        if (kpis.ml_model_metrics) {
            document.getElementById("ml-roc-auc").textContent = kpis.ml_model_metrics.roc_auc;
            document.getElementById("ml-accuracy").textContent = `${(kpis.ml_model_metrics.accuracy * 100).toFixed(1)}%`;
            document.getElementById("ml-f1").textContent = kpis.ml_model_metrics.f1_score;
        }

        // Macro ROI
        if (kpis.macro_roi) {
            document.getElementById("roi-penalties-saved").textContent = `₹${kpis.macro_roi.total_sla_penalties_saved_cr.toFixed(2)} Cr`;
            document.getElementById("roi-implementation-cost").textContent = `₹${kpis.macro_roi.total_implementation_cost_cr.toFixed(2)} Cr`;
            document.getElementById("roi-net-gain").textContent = `₹${kpis.macro_roi.net_financial_benefit_cr.toFixed(2)} Cr`;
            document.getElementById("roi-pct").textContent = `${kpis.macro_roi.macro_portfolio_roi_pct}%`;
            document.getElementById("roi-breach-drop").textContent = `-${kpis.macro_roi.deadline_breach_reduction_pct}%`;
        }
    } catch (err) {
        console.error("Error loading dashboard summary:", err);
    }
}

// -------------------------------------------------------------
// Cluster-Level Paper Capacity Paradox Chart
// -------------------------------------------------------------
async function loadClusterParadox() {
    try {
        const res = await fetch("/api/clusters");
        const json = await res.json();
        if (json.status !== "success") return;
        const clusters = json.data;

        const labels = clusters.map(c => c.cluster);
        const benchData = clusters.map(c => c.bench_headcount);
        const demandData = clusters.map(c => c.unfulfilled_demand);

        const ctx = document.getElementById("paradoxChart").getContext("2d");
        if (charts.paradox) charts.paradox.destroy();

        charts.paradox = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Gross Bench ('On Paper')",
                        data: benchData,
                        backgroundColor: "rgba(148, 163, 184, 0.65)",
                        borderColor: "#94a3b8",
                        borderWidth: 1.2,
                        borderRadius: 4
                    },
                    {
                        label: "Unfulfilled Project Demand",
                        data: demandData,
                        backgroundColor: "rgba(239, 68, 68, 0.75)",
                        borderColor: "#ef4444",
                        borderWidth: 1.2,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "#cbd5e1", font: { family: "Inter", size: 11, weight: "600" } }
                    },
                    tooltip: {
                        backgroundColor: "#0c172e",
                        titleColor: "#00d2ff",
                        borderColor: "rgba(0, 124, 195, 0.4)",
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#94a3b8", font: { size: 10.5 } },
                        grid: { color: "rgba(255, 255, 255, 0.04)" }
                    },
                    y: {
                        ticks: { color: "#94a3b8", font: { size: 10.5 } },
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        title: { display: true, text: "Headcount (Engineers)", color: "#94a3b8" }
                    }
                }
            }
        });

        // Delivery Unit Exposure Chart
        loadDuChart();
    } catch (err) {
        console.error("Error loading cluster paradox:", err);
    }
}

async function loadDuChart() {
    try {
        const res = await fetch("/api/projects");
        const json = await res.json();
        if (json.status !== "success") return;
        const projects = json.data;

        const duStats = {};
        projects.forEach(p => {
            const du = p.delivery_unit;
            if (!duStats[du]) {
                duStats[du] = { total: 0, breached: 0, penalties_cr: 0 };
            }
            duStats[du].total += 1;
            if (p.deadline_breached) {
                duStats[du].breached += 1;
                duStats[du].penalties_cr += (p.sla_penalty_incurred_lakhs / 100.0);
            }
        });

        const duLabelsMap = {
            "FS": "Financial Services",
            "MFG": "Manufacturing",
            "RCL": "Retail & CPG",
            "ECS": "Energy & Comm",
            "HLS": "Healthcare & Life"
        };

        const labels = Object.keys(duStats).map(k => duLabelsMap[k] || k);
        const breachedData = Object.values(duStats).map(s => s.breached);
        const penaltiesData = Object.values(duStats).map(s => s.penalties_cr);

        const ctx = document.getElementById("duExposureChart").getContext("2d");
        if (charts.du) charts.du.destroy();

        charts.du = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Breached Projects",
                        data: breachedData,
                        backgroundColor: "rgba(225, 29, 72, 0.75)",
                        borderColor: "#e11d48",
                        borderWidth: 1.2,
                        yAxisID: "y"
                    },
                    {
                        type: "line",
                        label: "SLA Penalties (₹ Cr)",
                        data: penaltiesData,
                        borderColor: "#f59e0b",
                        backgroundColor: "#f59e0b",
                        borderWidth: 2.2,
                        pointRadius: 4,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#cbd5e1", font: { family: "Inter", size: 11 } } }
                },
                scales: {
                    x: { ticks: { color: "#94a3b8", font: { size: 10 } }, grid: { display: false } },
                    y: {
                        type: "linear",
                        display: true,
                        position: "left",
                        ticks: { color: "#94a3b8" },
                        title: { display: true, text: "Breached Count", color: "#94a3b8" },
                        grid: { color: "rgba(255, 255, 255, 0.04)" }
                    },
                    y1: {
                        type: "linear",
                        display: true,
                        position: "right",
                        grid: { drawOnChartArea: false },
                        ticks: { color: "#f59e0b" },
                        title: { display: true, text: "Penalties (₹ Cr)", color: "#f59e0b" }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Error loading DU chart:", err);
    }
}

// -------------------------------------------------------------
// Skill Matrix & Critical Bottlenecks
// -------------------------------------------------------------
async function loadSkillMatrix() {
    try {
        const res = await fetch("/api/skills");
        const json = await res.json();
        if (json.status !== "success") return;
        allSkillsData = json.data;

        renderSkillTable(allSkillsData);
        renderCriticalSkillsChart(allSkillsData.slice(0, 8));

        // Setup filter
        const filterSelect = document.getElementById("skill-cluster-filter");
        filterSelect.addEventListener("change", (e) => {
            const cluster = e.target.value;
            if (cluster === "ALL") {
                renderSkillTable(allSkillsData);
            } else {
                renderSkillTable(allSkillsData.filter(s => s.cluster === cluster));
            }
        });
    } catch (err) {
        console.error("Error loading skill matrix:", err);
    }
}

function renderSkillTable(skills) {
    const tbody = document.getElementById("skills-table-body");
    tbody.innerHTML = "";

    skills.forEach(s => {
        const tr = document.createElement("tr");
        const netDeficitClass = s.net_gap < 0 ? "text-danger" : "text-success";
        const netDeficitText = s.net_gap < 0 ? `${s.net_gap}` : `+${s.net_gap}`;

        let ciBadge = "";
        if (s.criticality_index >= 30) {
            ciBadge = `<span class="badge badge-critical">CRITICAL (${s.criticality_index})</span>`;
        } else if (s.criticality_index >= 15) {
            ciBadge = `<span class="badge badge-hire">HIGH (${s.criticality_index})</span>`;
        } else if (s.criticality_index > 0) {
            ciBadge = `<span class="badge badge-upskill">MODERATE (${s.criticality_index})</span>`;
        } else {
            ciBadge = `<span class="badge badge-allocate">BALANCED</span>`;
        }

        tr.innerHTML = `
            <td><b>${s.skill_name}</b></td>
            <td><span style="color:#94a3b8; font-size:11.5px;">${s.cluster}</span></td>
            <td><span style="color:${s.scarcity > 0.8 ? '#ef4444' : '#38bdf8'}; font-weight:700;">${(s.scarcity * 100).toFixed(0)}%</span></td>
            <td>${s.bench_qualified}</td>
            <td>${s.rolling_qualified_30d}</td>
            <td><b>${s.unfulfilled_hc}</b></td>
            <td><b style="color: ${s.net_gap < 0 ? '#ef4444' : '#10b981'}">${netDeficitText}</b></td>
            <td>${ciBadge}</td>
            <td><span style="font-size:11px; color:#cbd5e1;">${s.bridge_from} (${s.bridge_days}d)</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderCriticalSkillsChart(topSkills) {
    const ctx = document.getElementById("criticalSkillsChart").getContext("2d");
    if (charts.critical) charts.critical.destroy();

    const labels = topSkills.map(s => s.skill_name);
    const ciValues = topSkills.map(s => s.criticality_index);

    charts.critical = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Criticality Index",
                data: ciValues,
                backgroundColor: "rgba(239, 68, 68, 0.75)",
                borderColor: "#ef4444",
                borderWidth: 1.2,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: "#0c172e", titleColor: "#00d2ff" }
            },
            scales: {
                x: {
                    ticks: { color: "#94a3b8" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    title: { display: true, text: "Criticality Index (Deficit × Scarcity × Revenue)", color: "#94a3b8" }
                },
                y: { ticks: { color: "#e2e8f0", font: { size: 11, weight: "600" } }, grid: { display: false } }
            }
        }
    });
}

// -------------------------------------------------------------
// Tri-Pillar Recommendations Loading
// -------------------------------------------------------------
async function loadRecommendations() {
    try {
        const res = await fetch("/api/recommendations");
        const json = await res.json();
        if (json.status !== "success") return;

        const recs = json.data;
        const macro = json.macro_roi;

        renderRecommendationsTable(recs);
        renderChannelPieChart(macro);

        // Filter button handling
        const filterBtns = document.querySelectorAll(".rec-filter-btn");
        filterBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                filterBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const action = btn.getAttribute("data-action");
                if (action === "ALL") {
                    renderRecommendationsTable(recs);
                } else {
                    renderRecommendationsTable(recs.filter(r => r.action_class === action));
                }
            });
        });
    } catch (err) {
        console.error("Error loading recommendations:", err);
    }
}

function renderRecommendationsTable(recs) {
    const tbody = document.getElementById("recs-table-body");
    tbody.innerHTML = "";

    recs.slice(0, 40).forEach(r => {
        const tr = document.createElement("tr");
        let badgeClass = "badge-allocate";
        if (r.action_class === "UPSKILL") badgeClass = "badge-upskill";
        else if (r.action_class === "HIRE") badgeClass = "badge-hire";
        else if (r.action_class === "HYBRID") badgeClass = "badge-hybrid";

        tr.innerHTML = `
            <td>
                <b>${r.project_name}</b><br/>
                <span style="font-size:11px; color:#64748b;">${r.project_id} | ${r.client_name} (${r.delivery_unit})</span>
            </td>
            <td>
                <b>${r.required_skill}</b><br/>
                <span style="font-size:11px; color:#94a3b8;">Gap: ${r.unfulfilled_headcount} Seats | SLA: ${r.staffing_deadline_days}d</span>
            </td>
            <td><span class="badge ${badgeClass}">${r.action_class}</span></td>
            <td>
                <span style="font-size:11.5px; color:#e2e8f0;">${r.strategic_action_summary}</span>
            </td>
            <td><b>${r.estimated_lead_time_days} days</b></td>
            <td>₹${r.estimated_cost_lakhs.toFixed(2)}L</td>
            <td><b style="color:#10b981;">₹${r.sla_penalty_saved_lakhs.toFixed(2)}L</b></td>
            <td><b style="color:#38bdf8;">+${r.net_roi_pct}%</b></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderChannelPieChart(macro) {
    const ctx = document.getElementById("channelPieChart").getContext("2d");
    if (charts.channel) charts.channel.destroy();

    charts.channel = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Internal Allocation", "Lex Upskilling", "External Hiring"],
            datasets: [{
                data: [
                    macro.allocated_internal_headcount,
                    macro.upskilled_headcount,
                    macro.external_hired_headcount
                ],
                backgroundColor: ["#10b981", "#0284c7", "#f59e0b"],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#cbd5e1", font: { family: "Inter", size: 11, weight: "600" }, padding: 12 }
                }
            },
            cutout: "68%"
        }
    });
}

// -------------------------------------------------------------
// Talent Matcher & Bench Console
// -------------------------------------------------------------
async function loadProjectDropdown() {
    try {
        const res = await fetch("/api/projects?breached_only=true");
        const json = await res.json();
        if (json.status !== "success") return;
        allProjectsData = json.data;

        const select = document.getElementById("matcher-project-select");
        select.innerHTML = '<option value="">-- Select an Open Client Project --</option>';

        allProjectsData.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.project_id;
            opt.textContent = `[${p.project_id}] ${p.project_name} (Skill: ${p.required_skill} | Gap: ${p.unfulfilled_headcount} | SLA: ${p.staffing_deadline_days}d)`;
            select.appendChild(opt);
        });

        select.addEventListener("change", (e) => {
            const prjId = e.target.value;
            if (prjId) {
                runTalentMatch(prjId);
            }
        });

        // Trigger first match automatically
        if (allProjectsData.length > 0) {
            select.value = allProjectsData[0].project_id;
            runTalentMatch(allProjectsData[0].project_id);
        }
    } catch (err) {
        console.error("Error loading projects for matcher:", err);
    }
}

async function runTalentMatch(projectId) {
    const container = document.getElementById("matcher-candidates-container");
    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #94a3b8;">Scanning 14,000 workforce records for optimal competency match...</div>`;

    try {
        const res = await fetch("/api/match_talent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId, top_n: 8 })
        });
        const json = await res.json();
        if (json.status !== "success") return;

        const prj = json.project;
        const risk = json.deadline_risk;
        const matches = json.matches;

        // Render Project Context Header
        document.getElementById("matcher-prj-name").textContent = prj.project_name;
        document.getElementById("matcher-prj-meta").textContent = `Client: ${prj.client_name} | Delivery Unit: ${prj.delivery_unit} | Target Location: ${prj.target_location}`;
        document.getElementById("matcher-prj-skill").textContent = prj.required_skill;
        document.getElementById("matcher-prj-sla").textContent = `${prj.staffing_deadline_days} Days Lead Time`;
        document.getElementById("matcher-prj-gap").textContent = `${prj.unfulfilled_headcount} Engineers Needed`;
        
        const riskBadge = document.getElementById("matcher-prj-risk");
        riskBadge.textContent = `${risk.risk_category} (${(risk.breach_probability * 100).toFixed(0)}%)`;
        riskBadge.className = `badge ${risk.predicted_breach ? 'badge-critical' : 'badge-allocate'}`;

        container.innerHTML = "";
        if (matches.length === 0) {
            container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 30px; color: #f59e0b;">No direct internal matches found. External hiring or intensive cross-cluster reskilling recommended.</div>`;
            return;
        }

        matches.forEach(m => {
            const card = document.createElement("div");
            card.className = "candidate-card";

            card.innerHTML = `
                <div class="cand-header">
                    <div>
                        <div class="cand-name">${m.full_name}</div>
                        <div class="cand-meta">${m.employee_id} • ${m.job_level} • ${m.base_location}</div>
                    </div>
                    <div class="match-score-badge">${m.composite_match_score}%</div>
                </div>

                <div style="font-size:12px; margin-bottom: 8px;">
                    <span style="color:#00d2ff; font-weight:700;">${m.primary_skill}</span> 
                    <span style="color:#94a3b8;">(Level ${m.proficiency_level})</span>
                </div>

                <div style="font-size:11.5px; color:#cbd5e1; margin-bottom: 10px;">
                    <b>Status:</b> ${m.availability_description}
                </div>

                <div class="score-bars">
                    <div class="bar-row">
                        <span>Skill Relevancy</span>
                        <div class="bar-container"><div class="bar-fill" style="width: ${m.skill_score}%;"></div></div>
                        <span>${m.skill_score}%</span>
                    </div>
                    <div class="bar-row">
                        <span>Proficiency Depth</span>
                        <div class="bar-container"><div class="bar-fill" style="width: ${m.prof_score}%;"></div></div>
                        <span>${m.prof_score}%</span>
                    </div>
                    <div class="bar-row">
                        <span>Availability Timing</span>
                        <div class="bar-container"><div class="bar-fill" style="width: ${m.avail_score}%;"></div></div>
                        <span>${m.avail_score}%</span>
                    </div>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; border-top:1px solid rgba(255,255,255,0.06); padding-top:10px;">
                    <span class="badge ${m.composite_match_score >= 80 ? 'badge-allocate' : 'badge-upskill'}">${m.fit_tier.split(' ')[0]} Match</span>
                    <button class="btn-action-small" onclick="alert('Candidate ${m.employee_id} queued for deployment confirmation with Project Lead.')">Allocate Now</button>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (err) {
        console.error("Error matching talent:", err);
    }
}

// -------------------------------------------------------------
// Interactive What-If Capacity Simulator
// -------------------------------------------------------------
function initSimulator() {
    const sVelocity = document.getElementById("sim-velocity");
    const sSurge = document.getElementById("sim-surge");
    const sCross = document.getElementById("sim-cross");
    const sBuffer = document.getElementById("sim-buffer");

    const vVelocity = document.getElementById("val-sim-velocity");
    const vSurge = document.getElementById("val-sim-surge");
    const vCross = document.getElementById("val-sim-cross");
    const vBuffer = document.getElementById("val-sim-buffer");

    let debounceTimer = null;

    function handleSliderChange() {
        vVelocity.textContent = `${sVelocity.value}%`;
        vSurge.textContent = `${sSurge.value} Specialists`;
        vCross.textContent = `${sCross.value}%`;
        vBuffer.textContent = `+${sBuffer.value} Days`;

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            triggerSimulation({
                upskilling_velocity_pct: parseFloat(sVelocity.value),
                contractor_surge_hc: parseInt(sSurge.value),
                cross_skilling_mobilization: parseFloat(sCross.value),
                sla_buffer_days: parseInt(sBuffer.value)
            });
        }, 150);
    }

    [sVelocity, sSurge, sCross, sBuffer].forEach(input => {
        input.addEventListener("input", handleSliderChange);
    });

    // Run initial simulation
    handleSliderChange();
}

async function triggerSimulation(params) {
    try {
        const res = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params)
        });
        const json = await res.json();
        if (json.status !== "success") return;
        const sim = json.simulation;

        // Update Simulated Display Metrics
        document.getElementById("sim-res-breaches").textContent = `${sim.simulated.breached_projects} (${sim.simulated.breach_rate_pct}%)`;
        document.getElementById("sim-res-penalties").textContent = `₹${sim.simulated.total_penalties_cr.toFixed(2)} Cr`;
        document.getElementById("sim-res-averted").textContent = `${sim.impact.breaches_averted} Projects (-${sim.impact.breach_reduction_pct}%)`;
        document.getElementById("sim-res-saved-penalties").textContent = `₹${sim.impact.sla_penalties_saved_cr.toFixed(2)} Cr`;
        document.getElementById("sim-res-cost").textContent = `₹${sim.impact.total_intervention_cost_cr.toFixed(2)} Cr`;
        document.getElementById("sim-res-net-savings").textContent = `₹${sim.impact.net_financial_savings_cr.toFixed(2)} Cr`;
        document.getElementById("sim-res-utilization").textContent = `${sim.simulated.bench_utilization_pct}% (+${sim.impact.utilization_gain_bps} bps)`;

        renderSimComparisonChart(sim);
    } catch (err) {
        console.error("Error triggering simulation:", err);
    }
}

function renderSimComparisonChart(sim) {
    const ctx = document.getElementById("simCompareChart").getContext("2d");
    if (charts.simCompare) charts.simCompare.destroy();

    charts.simCompare = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Breached Projects Count", "SLA Penalties (₹ Cr)", "Bench Utilization (%)"],
            datasets: [
                {
                    label: "Baseline State (As-Is)",
                    data: [sim.baseline.breached_projects, sim.baseline.total_penalties_cr, sim.baseline.bench_utilization_pct],
                    backgroundColor: "rgba(239, 68, 68, 0.65)",
                    borderColor: "#ef4444",
                    borderWidth: 1.2
                },
                {
                    label: "Simulated Post-AI State",
                    data: [sim.simulated.breached_projects, sim.simulated.total_penalties_cr, sim.simulated.bench_utilization_pct],
                    backgroundColor: "rgba(16, 185, 129, 0.75)",
                    borderColor: "#10b981",
                    borderWidth: 1.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: "#cbd5e1", font: { family: "Inter", size: 11, weight: "600" } } }
            },
            scales: {
                x: { ticks: { color: "#94a3b8", font: { size: 11 } }, grid: { display: false } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255, 255, 255, 0.04)" } }
            }
        }
    });
}

