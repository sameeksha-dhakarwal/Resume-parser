document.getElementById("uploadBtn").addEventListener("click", uploadFile);

// Global state for deletable contact fields
let contactState = {};

async function uploadFile() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Please select a file first.");

  const uploadBtn = document.getElementById("uploadBtn");
  uploadBtn.textContent = "Parsing...";
  uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    render(data);
  } catch (err) {
    alert("Error connecting to server. Make sure Flask is running.");
    console.error(err);
  } finally {
    uploadBtn.textContent = "Upload & Parse";
    uploadBtn.disabled = false;
  }
}


// ─── RENDER ──────────────────────────────────────────────────────────────────
function render(data) {
  const output = document.getElementById("output");
  const s = data.sections || {};

  // Legacy getter for sections not handled by AI
  const get = (keys) => {
    for (let key of keys) {
      if (s[key]) return s[key].join("\n");
    }
    return "";
  };

  // Initialize contact state from API
  const contact = data.contact || {};
  contactState = {
    name:     { value: contact.name || "",     label: "👤 Name",     visible: !!contact.name },
    email:    { value: contact.email || "",    label: "✉️ Email",    visible: !!contact.email },
    phone:    { value: contact.phone || "",    label: "📞 Phone",    visible: !!contact.phone },
    linkedin: { value: contact.linkedin || "", label: "🔗 LinkedIn", visible: !!contact.linkedin },
    github:   { value: contact.github || "",   label: "🐙 GitHub",   visible: !!contact.github },
    leetcode: { value: contact.leetcode || "", label: "💡 LeetCode", visible: !!contact.leetcode },
  };

  // Add other_links to contactState
  (contact.other_links || []).forEach((link, i) => {
    contactState[`other_${i}`] = { value: link, label: "🌐 Link", visible: true };
  });

  // Fallback to raw text for summary/education/skills
  const aiData = data.ai_data || {};

  const summary = aiData.summary || get(["SUMMARY", "ABOUT ME", "PROFESSIONAL SUMMARY"]) || "";
  const education = aiData.education || get(["EDUCATION"]) || "";

  // Certifications and responsibilities come as arrays from the backend
  const certLines = data.certifications || [];
  const respLines = data.responsibilities || [];

  // Skills
  const skillsList = data.skills || [];
  const skillsText = skillsList.length > 0
    ? skillsList.join("\n")
    : (aiData.skills || get(["SKILLS", "TECHNICAL SKILLS"]) || "");

  output.innerHTML = `
    <div class="page">

      <!-- FILE INFO -->
      <div class="card highlight file-info">
        <h2>📄 File Info</h2>
        <p><b>Type:</b> ${data.file_info.type}</p>
        <p><b>Size:</b> ${data.file_info.size} KB</p>
        ${data.ats_score ? `<p><b>ATS Score:</b> <span class="ats-score">${data.ats_score}/100</span></p>` : ""}
      </div>

      <div class="custom-grid">

        <!-- CONTACT (with delete boxes) -->
        <div class="card" id="contact-card">
          <h2>👤 PROFILE</h2>
          <div id="contact-fields" class="contact-fields">
            ${renderContactFields()}
          </div>
        </div>

        <!-- PROFESSIONAL SUMMARY -->
        <div class="card">
          <h2>🧾 PROFESSIONAL SUMMARY</h2>
          <pre>${escHtml(summary) || "<em>Not found</em>"}</pre>
        </div>

        <!-- EDUCATION -->
        <div class="card">
          <h2>🎓 EDUCATION</h2>
          ${renderEducation(data.structured_education, education)}
        </div>

        <!-- SKILLS -->
        <div class="card">
          <h2>🛠 SKILLS</h2>
          ${renderSkills(data.structured_skills, skillsText)}
        </div>

        <!-- EXPERIENCE (AI summarized) -->
        <div class="card">
          <h2>💼 EXPERIENCE</h2>
          ${renderExperience(data.experience)}
        </div>

        <!-- PROJECTS (AI summarized) -->
        <div class="card">
          <h2>🚀 PROJECTS</h2>
          ${renderProjects(data.projects)}
        </div>

        <!-- CERTIFICATIONS -->
        <div class="card">
          <h2>📜 CERTIFICATIONS</h2>
          ${renderBulletList(certLines, "No certifications found")}
        </div>

        <!-- RESPONSIBILITIES -->
        <div class="card">
          <h2>🏅 RESPONSIBILITIES</h2>
          ${renderBulletList(respLines, "No responsibilities found")}
        </div>

      </div>
    </div>
  `;

  // Attach delete handlers
  attachContactDeleteHandlers();
}


// ─── CONTACT FIELDS ──────────────────────────────────────────────────────────
function renderContactFields() {
  return Object.entries(contactState)
    .filter(([, v]) => v.visible && v.value)
    .map(([key, v]) => `
      <div class="contact-chip" id="chip-${key}">
        <span class="chip-label">${v.label}</span>
        <span class="chip-value">${isUrl(v.value)
          ? `<a href="${v.value}" target="_blank" rel="noopener">${v.value}</a>`
          : escHtml(v.value)
        }</span>
        <button class="delete-chip" data-key="${key}" title="Remove this field">✕</button>
      </div>
    `).join("");
}

function attachContactDeleteHandlers() {
  document.querySelectorAll(".delete-chip").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const key = e.target.getAttribute("data-key");
      if (contactState[key]) {
        contactState[key].visible = false;
        document.getElementById(`chip-${key}`)?.remove();
      }
    });
  });
}

function isUrl(str) {
  return /^https?:\/\//i.test(str) || /linkedin\.com|github\.com|leetcode\.com/i.test(str);
}


// ─── EXPERIENCE ──────────────────────────────────────────────────────────────
function renderExperience(experiences) {
  if (!experiences || experiences.length === 0) {
    // Fallback: show raw text
    return `<pre>Not found or still parsing...</pre>`;
  }

  return experiences.map(exp => `
    <div class="exp-entry">
      <div class="exp-header">
        <span class="exp-role">${escHtml(exp.role || "")}</span>
        ${exp.duration ? `<span class="exp-duration">(${escHtml(exp.duration)})</span>` : ""}
      </div>
      <div class="exp-company">${escHtml(exp.company || "")}</div>
      <ul class="exp-bullets">
        ${(exp.summary || []).map(pt => `<li>${escHtml(pt)}</li>`).join("")}
      </ul>
    </div>
  `).join('<hr class="entry-divider">');
}


// ─── PROJECTS ────────────────────────────────────────────────────────────────
function renderProjects(projects) {
  if (!projects || projects.length === 0) {
    return `<pre>Not found or still parsing...</pre>`;
  }

  return projects.map(proj => `
    <div class="proj-entry">
      <div class="proj-title">🔷 ${escHtml(proj.title || "Untitled Project")}</div>
      ${proj.tech_stack && proj.tech_stack.length > 0
        ? `<div class="proj-stack">
            ${proj.tech_stack.map(t => `<span class="tech-badge">${escHtml(t)}</span>`).join("")}
           </div>`
        : ""
      }
      <ul class="proj-bullets">
        ${(proj.description || []).map(pt => `<li>${escHtml(pt)}</li>`).join("")}
      </ul>
    </div>
  `).join('<hr class="entry-divider">');
}


// ─── EDUCATION ────────────────────────────────────────────────────────────────
function renderEducation(entries, fallbackText) {
  if (!entries || entries.length === 0) {
    // Fallback: raw text as plain pre
    return fallbackText
      ? `<pre>${escHtml(fallbackText)}</pre>`
      : `<p><em>Not found</em></p>`;
  }

  return entries.map(entry => `
    <div class="edu-entry">
      <div class="edu-institution">🏛 ${escHtml(entry.institution || "")}</div>
      <div class="edu-degree">${escHtml(entry.degree || "")}</div>
      <div class="edu-meta">
        ${entry.grade ? `<span class="edu-grade">📊 ${escHtml(entry.grade)}</span>` : ""}
        ${entry.duration ? `<span class="edu-duration">📅 ${escHtml(entry.duration)}</span>` : ""}
      </div>
    </div>
  `).join('<hr class="entry-divider">');
}


// ─── SKILLS ───────────────────────────────────────────────────────────────────
function renderSkills(categories, fallbackText) {
  if (!categories || categories.length === 0) {
    // Fallback: raw text
    return fallbackText
      ? `<pre>${escHtml(fallbackText)}</pre>`
      : `<p><em>Not found</em></p>`;
  }

  return categories.map(cat => `
    <div class="skill-category">
      <div class="skill-cat-label">${escHtml(cat.category || "Other")}</div>
      <div class="skill-chips">
        ${(cat.skills || []).map(s => `<span class="skill-chip">${escHtml(s)}</span>`).join("")}
      </div>
    </div>
  `).join("");
}


// ─── BULLET LIST (certifications, responsibilities) ───────────────────────────
function renderBulletList(lines, emptyMsg) {
  if (!lines || lines.length === 0) {
    return `<p><em>${emptyMsg || "Not found"}</em></p>`;
  }
  return `
    <ul class="generic-bullets">
      ${lines.map(l => `<li>${escHtml(l)}</li>`).join("")}
    </ul>
  `;
}


// ─── HELPERS ─────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}