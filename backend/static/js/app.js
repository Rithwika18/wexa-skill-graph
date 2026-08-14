/**
 * WEXA Skill Graph — Frontend Application Logic
 * Vanilla JavaScript communicating with Flask REST APIs via fetch()
 */

document.addEventListener("DOMContentLoaded", () => {
    // =========================================================================
    // STATE & DOM ELEMENTS
    // =========================================================================
    let allSkills = [];
    let availableRoles = [];
    let lastExtractedSkills = [];

    // Header & Database Status
    const dbStatusBadge = document.getElementById("db-status-badge");
    const dbStatusText = document.getElementById("db-status-text");

    // Global Alert
    const globalAlert = document.getElementById("global-alert");
    const alertMessage = document.getElementById("alert-message");
    const alertClose = document.getElementById("alert-close");

    // Tabs
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    // Section 1: Roles Elements
    const roleSelect = document.getElementById("role-select");
    const roleMetaBadge = document.getElementById("role-meta-badge");
    const roleDomainTag = document.getElementById("role-domain-tag");
    const roleLevelTag = document.getElementById("role-level-tag");
    const skillsCheckboxGrid = document.getElementById("skills-checkbox-grid");
    const btnSelectAllSkills = document.getElementById("btn-select-all-skills");
    const btnClearSkills = document.getElementById("btn-clear-skills");
    const btnGenerateRoadmap = document.getElementById("btn-generate-roadmap");
    const rolesLoading = document.getElementById("roles-loading");
    const rolesEmpty = document.getElementById("roles-empty");
    const rolesResult = document.getElementById("roles-result");
    const readinessBadge = document.getElementById("readiness-badge");
    const readinessProgress = document.getElementById("readiness-progress");
    const acquiredCount = document.getElementById("acquired-count");
    const acquiredSkillsTags = document.getElementById("acquired-skills-tags");
    const missingReqCount = document.getElementById("missing-req-count");
    const missingReqTags = document.getElementById("missing-req-tags");
    const roadmapTimeline = document.getElementById("roadmap-timeline");

    // Section 2: NLP Elements
    const nlpInputText = document.getElementById("nlp-input-text");
    const btnSampleNlp = document.getElementById("btn-sample-nlp");
    const btnExtractSkills = document.getElementById("btn-extract-skills");
    const nlpLoading = document.getElementById("nlp-loading");
    const nlpEmpty = document.getElementById("nlp-empty");
    const nlpResult = document.getElementById("nlp-result");
    const nlpExtractedCount = document.getElementById("nlp-extracted-count");
    const nlpTableBody = document.getElementById("nlp-table-body");
    const btnApplyToRoles = document.getElementById("btn-apply-to-roles");

    // Section 3: Graph Traversal Elements
    const reachableStartSkill = document.getElementById("reachable-start-skill");
    const reachableMinHops = document.getElementById("reachable-min-hops");
    const reachableMaxHops = document.getElementById("reachable-max-hops");
    const btnRunReachable = document.getElementById("btn-run-reachable");
    const reachableLoading = document.getElementById("reachable-loading");
    const reachableEmpty = document.getElementById("reachable-empty");
    const reachableResult = document.getElementById("reachable-result");
    const reachableTags = document.getElementById("reachable-tags");

    const commonSkill1 = document.getElementById("common-skill-1");
    const commonSkill2 = document.getElementById("common-skill-2");
    const btnRunCommon = document.getElementById("btn-run-common");
    const commonLoading = document.getElementById("common-loading");
    const commonEmpty = document.getElementById("common-empty");
    const commonResult = document.getElementById("common-result");
    const commonTableBody = document.getElementById("common-table-body");

    // =========================================================================
    // UTILITY & ALERT HELPERS
    // =========================================================================
    function showAlert(msg) {
        alertMessage.textContent = msg;
        globalAlert.classList.remove("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function hideAlert() {
        globalAlert.classList.add("hidden");
    }

    alertClose.addEventListener("click", hideAlert);

    // =========================================================================
    // TAB SWITCHING
    // =========================================================================
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-tab");

            tabButtons.forEach(btn => {
                btn.classList.remove("active");
                btn.setAttribute("aria-selected", "false");
            });
            tabPanes.forEach(pane => pane.classList.remove("active"));

            button.classList.add("active");
            button.setAttribute("aria-selected", "true");
            document.getElementById(targetId).classList.add("active");
            hideAlert();
        });
    });

    // =========================================================================
    // INITIAL DATA LOADING & HEALTH CHECKS
    // =========================================================================
    async function checkDatabaseHealth() {
        try {
            const res = await fetch("/api/health/db");
            const data = await res.json();

            if (res.ok && data.status === "connected") {
                dbStatusBadge.className = "status-badge status-online";
                dbStatusText.textContent = "CognoDB Live (Bolt)";
            } else {
                dbStatusBadge.className = "status-badge status-fallback";
                dbStatusText.textContent = "In-Memory Fallback";
            }
        } catch (e) {
            dbStatusBadge.className = "status-badge status-fallback";
            dbStatusText.textContent = "In-Memory Mode";
        }
    }

    async function loadSkillsAndRoles() {
        try {
            // 1. Fetch all skills
            const skillsRes = await fetch("/api/skills");
            const skillsData = await skillsRes.json();
            allSkills = skillsData.skills || [];

            // Populate Checkbox Grid
            skillsCheckboxGrid.innerHTML = "";
            allSkills.forEach(skill => {
                const label = document.createElement("label");
                label.className = "skill-checkbox-label";
                label.innerHTML = `
                    <input type="checkbox" value="${skill}" class="user-skill-cb">
                    <span>${skill}</span>
                `;
                skillsCheckboxGrid.appendChild(label);
            });

            // Populate Traversal Dropdowns
            reachableStartSkill.innerHTML = '<option value="">-- Select Starting Skill --</option>';
            commonSkill1.innerHTML = '<option value="">-- Select Skill 1 --</option>';
            commonSkill2.innerHTML = '<option value="">-- Select Skill 2 --</option>';

            allSkills.forEach(skill => {
                reachableStartSkill.innerHTML += `<option value="${skill}">${skill}</option>`;
                commonSkill1.innerHTML += `<option value="${skill}">${skill}</option>`;
                commonSkill2.innerHTML += `<option value="${skill}">${skill}</option>`;
            });

            // Default selections for convenience
            if (allSkills.includes("Python")) reachableStartSkill.value = "Python";
            if (allSkills.includes("NLP")) commonSkill1.value = "NLP";
            if (allSkills.includes("PyTorch")) commonSkill2.value = "PyTorch";

            // 2. Fetch all roles
            const rolesRes = await fetch("/api/roles");
            const rolesData = await rolesRes.json();
            availableRoles = rolesData.roles || [];

            roleSelect.innerHTML = '<option value="">-- Select a Career Role --</option>';
            availableRoles.forEach(role => {
                roleSelect.innerHTML += `<option value="${role.title}">${role.title} (${role.domain})</option>`;
            });

            if (availableRoles.length > 0) {
                btnGenerateRoadmap.disabled = false;
            }
        } catch (err) {
            showAlert("Failed to initialize skills taxonomy from backend: " + err.message);
        }
    }

    // Role Selection Change handler
    roleSelect.addEventListener("change", () => {
        const selectedTitle = roleSelect.value;
        const role = availableRoles.find(r => r.title === selectedTitle);

        if (role) {
            roleDomainTag.textContent = `Domain: ${role.domain}`;
            roleLevelTag.textContent = `Level: ${role.level}`;
            roleMetaBadge.classList.remove("hidden");
            btnGenerateRoadmap.disabled = false;
        } else {
            roleMetaBadge.classList.add("hidden");
            btnGenerateRoadmap.disabled = true;
        }
    });

    btnSelectAllSkills.addEventListener("click", () => {
        document.querySelectorAll(".user-skill-cb").forEach(cb => cb.checked = true);
    });

    btnClearSkills.addEventListener("click", () => {
        document.querySelectorAll(".user-skill-cb").forEach(cb => cb.checked = false);
    });

    // =========================================================================
    // SECTION 1: GENERATE ROLE LEARNING ROADMAP
    // =========================================================================
    btnGenerateRoadmap.addEventListener("click", async () => {
        const targetRole = roleSelect.value;
        if (!targetRole) {
            showAlert("Please select a target career role first.");
            return;
        }

        const selectedSkills = Array.from(document.querySelectorAll(".user-skill-cb:checked"))
            .map(cb => cb.value);

        hideAlert();
        rolesEmpty.classList.add("hidden");
        rolesResult.classList.add("hidden");
        rolesLoading.classList.remove("hidden");

        try {
            const res = await fetch("/api/recommendations/role-path", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    target_role: targetRole,
                    user_skills: selectedSkills
                })
            });

            const data = await res.json();
            rolesLoading.classList.add("hidden");

            if (!res.ok) {
                showAlert(data.error || "Failed to calculate role roadmap.");
                rolesEmpty.classList.remove("hidden");
                return;
            }

            renderRoleRoadmap(data);
        } catch (err) {
            rolesLoading.classList.add("hidden");
            rolesEmpty.classList.remove("hidden");
            showAlert("Network error while generating roadmap: " + err.message);
        }
    });

    function renderRoleRoadmap(data) {
        rolesResult.classList.remove("hidden");

        // 1. Readiness Score
        const pct = data.readiness_percentage || 0;
        readinessProgress.style.width = `${pct}%`;
        readinessBadge.textContent = `${pct}% Match`;

        if (pct >= 80) {
            readinessBadge.className = "badge badge-success";
        } else if (pct >= 40) {
            readinessBadge.className = "badge badge-warning";
        } else {
            readinessBadge.className = "badge badge-danger";
        }

        // 2. Acquired Skills
        acquiredCount.textContent = data.acquired_skills.length;
        acquiredSkillsTags.innerHTML = "";
        if (data.acquired_skills.length === 0) {
            acquiredSkillsTags.innerHTML = "<span class='info-note'>None yet</span>";
        } else {
            data.acquired_skills.forEach(skill => {
                acquiredSkillsTags.innerHTML += `<span class="pill-tag pill-acquired">✓ ${skill}</span>`;
            });
        }

        // 3. Missing Required Skills
        missingReqCount.textContent = data.missing_required_skills.length;
        missingReqTags.innerHTML = "";
        if (data.missing_required_skills.length === 0) {
            missingReqTags.innerHTML = "<span class='info-note'>All required skills acquired! 🎉</span>";
        } else {
            data.missing_required_skills.forEach(skill => {
                missingReqTags.innerHTML += `<span class="pill-tag pill-missing">! ${skill}</span>`;
            });
        }

        // 4. Milestone Timeline
        roadmapTimeline.innerHTML = "";
        const roadmap = data.learning_roadmap || [];

        if (roadmap.length === 0) {
            roadmapTimeline.innerHTML = `
                <div class="empty-state-sm">
                    <p>🎉 You already possess all prerequisite competencies for this role!</p>
                </div>
            `;
        } else {
            roadmap.forEach(milestone => {
                const stepEl = document.createElement("div");
                stepEl.className = "timeline-step";

                let detailsHtml = "";
                if (milestone.skill_details) {
                    detailsHtml = milestone.skill_details.map(d => {
                        const prereqs = d.prerequisites.length > 0
                            ? `(Prerequisites: ${d.prerequisites.join(", ")})`
                            : `(Foundational Root Skill)`;
                        return `<div class="timeline-skill-item"><strong>${d.skill}</strong> <span class="info-note">${prereqs}</span></div>`;
                    }).join("");
                } else {
                    detailsHtml = milestone.skills.map(s => `<div class="timeline-skill-item"><strong>${s}</strong></div>`).join("");
                }

                stepEl.innerHTML = `
                    <div class="timeline-marker">${milestone.step}</div>
                    <div class="timeline-card">
                        <div class="timeline-title">Milestone Stage ${milestone.step} (${milestone.skills.length} skills)</div>
                        ${detailsHtml}
                    </div>
                `;
                roadmapTimeline.appendChild(stepEl);
            });
        }
    }

    // =========================================================================
    // SECTION 2: AI SKILL EXTRACTOR
    // =========================================================================
    btnSampleNlp.addEventListener("click", () => {
        nlpInputText.value = "We are seeking a Machine Learning Engineer with strong proficiency in Python, SQL, and Pandas. Candidates must have hands-on experience in Data Analysis, Deep Learning, and model training using PyTorch or NLP techniques.";
    });

    btnExtractSkills.addEventListener("click", async () => {
        const text = nlpInputText.value.trim();
        if (!text) {
            showAlert("Please enter or paste text to extract skills from.");
            return;
        }

        hideAlert();
        nlpEmpty.classList.add("hidden");
        nlpResult.classList.add("hidden");
        nlpLoading.classList.remove("hidden");

        try {
            const res = await fetch("/api/skills/extract", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });

            const data = await res.json();
            nlpLoading.classList.add("hidden");

            if (!res.ok) {
                showAlert(data.error || "Skill extraction failed.");
                nlpEmpty.classList.remove("hidden");
                return;
            }

            renderNlpResults(data);
        } catch (err) {
            nlpLoading.classList.add("hidden");
            nlpEmpty.classList.remove("hidden");
            showAlert("Error during skill extraction: " + err.message);
        }
    });

    function renderNlpResults(data) {
        nlpResult.classList.remove("hidden");
        const normalized = data.normalized_skills || [];
        lastExtractedSkills = data.canonical_skills || [];

        nlpExtractedCount.textContent = data.count || 0;
        nlpTableBody.innerHTML = "";

        if (normalized.length === 0) {
            nlpTableBody.innerHTML = `<tr><td colspan="3" class="text-muted text-center">No recognizable skills detected in the text.</td></tr>`;
            return;
        }

        normalized.forEach(item => {
            const statusBadge = item.in_graph
                ? `<span class="badge badge-success">✓ In Graph</span>`
                : `<span class="badge badge-warning">Unseeded</span>`;

            nlpTableBody.innerHTML += `
                <tr>
                    <td><code>${item.raw}</code></td>
                    <td><strong>${item.canonical}</strong></td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        });
    }

    btnApplyToRoles.addEventListener("click", () => {
        if (lastExtractedSkills.length === 0) {
            showAlert("No extracted skills available to transfer.");
            return;
        }

        // Check matching checkboxes in Section 1
        document.querySelectorAll(".user-skill-cb").forEach(cb => {
            if (lastExtractedSkills.includes(cb.value)) {
                cb.checked = true;
            }
        });

        // Switch to Roles Tab
        document.querySelector('[data-tab="tab-roles"]').click();
        showAlert(`Applied ${lastExtractedSkills.length} extracted skills to your profile! Select a role to continue.`);
    });

    // =========================================================================
    // SECTION 3: GRAPH TRAVERSALS
    // =========================================================================
    btnRunReachable.addEventListener("click", async () => {
        const skill = reachableStartSkill.value;
        if (!skill) {
            showAlert("Please select a starting skill for traversal.");
            return;
        }

        const minHops = reachableMinHops.value || 1;
        const maxHops = reachableMaxHops.value || 3;

        reachableEmpty.classList.add("hidden");
        reachableResult.classList.add("hidden");
        reachableLoading.classList.remove("hidden");
        hideAlert();

        try {
            const res = await fetch(`/api/skills/${encodeURIComponent(skill)}/reachable?min_hops=${minHops}&max_hops=${maxHops}`);
            const data = await res.json();
            reachableLoading.classList.add("hidden");

            if (!res.ok) {
                showAlert(data.error || "Failed to execute multi-hop traversal.");
                reachableEmpty.classList.remove("hidden");
                return;
            }

            reachableResult.classList.remove("hidden");
            reachableTags.innerHTML = "";

            const skills = data.reachable_skills || [];
            if (skills.length === 0) {
                reachableTags.innerHTML = `<span class="info-note">No downstream skills reachable within ${minHops} to ${maxHops} hops.</span>`;
            } else {
                skills.forEach(s => {
                    reachableTags.innerHTML += `
                        <span class="pill-tag pill-hop">
                            ${s.skill} <span class="badge" style="background:#e0e7ff; color:#3730a3;">+${s.distance} Hops</span>
                        </span>
                    `;
                });
            }
        } catch (err) {
            reachableLoading.classList.add("hidden");
            reachableEmpty.classList.remove("hidden");
            showAlert("Error running traversal query: " + err.message);
        }
    });

    btnRunCommon.addEventListener("click", async () => {
        const s1 = commonSkill1.value;
        const s2 = commonSkill2.value;

        if (!s1 || !s2) {
            showAlert("Please select both target skills.");
            return;
        }

        if (s1 === s2) {
            showAlert("Please select two distinct skills.");
            return;
        }

        commonEmpty.classList.add("hidden");
        commonResult.classList.add("hidden");
        commonLoading.classList.remove("hidden");
        hideAlert();

        try {
            const res = await fetch(`/api/skills/common-prerequisites?skill1=${encodeURIComponent(s1)}&skill2=${encodeURIComponent(s2)}`);
            const data = await res.json();
            commonLoading.classList.add("hidden");

            if (!res.ok) {
                showAlert(data.error || "Failed to find common prerequisites.");
                commonEmpty.classList.remove("hidden");
                return;
            }

            commonResult.classList.remove("hidden");
            commonTableBody.innerHTML = "";

            const prereqs = data.common_prerequisites || [];
            if (prereqs.length === 0) {
                commonTableBody.innerHTML = `<tr><td colspan="4" class="text-muted text-center">No common prerequisite foundation found.</td></tr>`;
            } else {
                prereqs.forEach(item => {
                    commonTableBody.innerHTML += `
                        <tr>
                            <td><strong>${item.skill}</strong></td>
                            <td>${item.dist_to_skill1} hop(s)</td>
                            <td>${item.dist_to_skill2} hop(s)</td>
                            <td><span class="badge badge-warning">${item.total_distance} total hops</span></td>
                        </tr>
                    `;
                });
            }
        } catch (err) {
            commonLoading.classList.add("hidden");
            commonEmpty.classList.remove("hidden");
            showAlert("Error finding common prerequisites: " + err.message);
        }
    });

    // =========================================================================
    // INIT
    // =========================================================================
    checkDatabaseHealth();
    loadSkillsAndRoles();
});
