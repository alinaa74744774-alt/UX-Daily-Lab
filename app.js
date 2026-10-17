(() => {
  "use strict";
  const sourcePath = "Day01_User_Research_Interview_Plan.md";
  const sourceUrl = `./${encodeURIComponent(sourcePath)}`;
  const sourceOnGitHub = "https://github.com/alinaa74744774-alt/UX-Daily-Lab/blob/main/Day01_User_Research_Interview_Plan.md";
  const days = [
    ["01", "User Research", "用户研究", "Active"],
    ["02", "User Persona", "用户画像", "Upcoming"],
    ["03", "Information Architecture", "信息架构", "Upcoming"],
    ["04", "User Flow", "用户流程", "Upcoming"],
    ["05", "UI Design", "界面设计", "Upcoming"],
    ["06", "Interactive Prototype", "交互原型", "Upcoming"],
    ["07", "Weekly Review", "每周复盘", "Locked"]
  ];
  const nav = document.getElementById("weekNav");
  nav.innerHTML = days.map((day, index) => `<a class="day-link ${index === 0 ? "active" : ""}" href="${index === 0 ? "#top" : "#"}" data-day-index="${index}" ${index === 0 ? 'aria-current="page"' : 'aria-haspopup="dialog"'}><span class="day-num">${day[0]}</span><span class="day-title">${day[1]}<small>${day[2]}</small></span><span class="day-status" title="${day[3]}">${index === 0 ? "●" : index === 6 ? "◌" : "↗"}</span></a>`).join("");
  nav.insertAdjacentHTML("beforeend", '<div class="week-note">WEEK 01 <span>1 active · 6 upcoming</span></div>');

  const escapeHtml = (value) => value.replace(/[&<>\"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[char]));
  const inline = (value) => escapeHtml(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");

  function renderMarkdown(markdown) {
    const lines = markdown.replace(/\r/g, "").split("\n");
    let html = "", list = "", quote = false, table = false;
    const closeList = () => { if (list) { html += `</${list}>`; list = ""; } };
    const closeQuote = () => { if (quote) { html += "</blockquote>"; quote = false; } };
    const closeTable = () => { if (table) { html += "</tbody></table>"; table = false; } };
    for (const raw of lines) {
      const line = raw.trim();
      if (!line) { closeList(); closeQuote(); closeTable(); continue; }
      if (/^\|.*\|$/.test(line)) {
        closeList(); closeQuote();
        const cells = line.slice(1, -1).split("|").map((cell) => cell.trim());
        if (cells.every((cell) => /^:?-{3,}:?$/.test(cell))) continue;
        if (!table) {
          html += `<table><thead><tr>${cells.map((cell) => `<th>${inline(cell)}</th>`).join("")}</tr></thead><tbody>`;
          table = true;
        } else {
          html += `<tr>${cells.map((cell) => `<td>${inline(cell)}</td>`).join("")}</tr>`;
        }
        continue;
      }
      closeTable();
      if (/^#{1,4}\s/.test(line)) {
        closeList(); closeQuote();
        const match = line.match(/^(#{1,4})\s+(.*)$/);
        const level = match[1].length;
        html += `<h${level}>${inline(match[2])}</h${level}>`;
        continue;
      }
      if (/^---+$/.test(line)) { closeList(); closeQuote(); html += "<hr>"; continue; }
      if (/^>\s?/.test(line)) {
        closeList();
        if (!quote) { html += "<blockquote>"; quote = true; }
        html += `<p>${inline(line.replace(/^>\s?/, ""))}</p>`;
        continue;
      }
      closeQuote();
      const unordered = line.match(/^[-*]\s+(.*)$/);
      const ordered = line.match(/^\d+\.\s+(.*)$/);
      if (unordered || ordered) {
        const kind = unordered ? "ul" : "ol";
        if (list !== kind) { closeList(); html += `<${kind}>`; list = kind; }
        html += `<li>${inline((unordered || ordered)[1])}</li>`;
        continue;
      }
      closeList();
      html += `<p>${inline(line)}</p>`;
    }
    closeList(); closeQuote(); closeTable();
    return html;
  }

  function extractSection(markdown, heading) {
    const lines = markdown.split("\n");
    const start = lines.findIndex((line) => line.trim() === heading);
    if (start < 0) return "";
    let end = start + 1;
    while (end < lines.length && !/^##\s/.test(lines[end])) end++;
    return lines.slice(start + 1, end).join("\n").trim();
  }

  function parseVocab(markdown) {
    const section = extractSection(markdown, "## UX English Learning｜UX 专业英语学习");
    const terms = [...section.matchAll(/^###\s+\d+\.\s+(.+)$/gm)];
    return terms.map((term, index) => {
      const start = term.index + term[0].length;
      const end = terms[index + 1]?.index ?? section.length;
      const body = section.slice(start, end);
      const field = (pattern) => body.match(pattern)?.[1]?.trim() || "";
      const english = field(/^- \*\*Definition:\*\*\s*(.+)$/m);
      const chinese = field(/^\s*中文解释：(.+)$/m);
      const example = field(/^- \*\*UX example:\*\*\s*“?(.+?)”?\s*$/m);
      const translation = field(/^\s*例句理解：(.+)$/m);
      const title = term[1].trim();
      const split = title.lastIndexOf(" ");
      const englishTerm = split > 0 ? title.slice(0, split) : title;
      const chineseTerm = split > 0 ? title.slice(split + 1) : "";
      return `<article class="vocab-card"><div class="vocab-title"><span class="vocab-index">0${index + 1}</span><h3>${escapeHtml(englishTerm)}</h3><span class="vocab-term-zh">${escapeHtml(chineseTerm)}</span></div><div class="vocab-field"><b>ENGLISH DEFINITION</b><p class="vocab-def">${escapeHtml(english)}</p></div><div class="vocab-field vocab-support"><b>中文理解</b><p class="vocab-zh">${escapeHtml(chinese)}</p></div><div class="vocab-example"><b>UX CONTEXT EXAMPLE</b><p>“${escapeHtml(example.replace(/^“|”$/g, ""))}”</p><small>中文例句理解｜${escapeHtml(translation)}</small></div></article>`;
    }).join("");
  }

  function renderPhrases(markdown) {
    const section = extractSection(markdown, "### Phrases to remember｜值得记忆的表达");
    const phrases = [...section.matchAll(/^- \*\*“([^”]+)”\*\* — (.+)$/gm)];
    return phrases.map((phrase) => {
      const nextLine = section.slice(phrase.index + phrase[0].length).match(/^\s*中文理解：(.+)$/m)?.[1] || "";
      return `<div class="phrase-item"><span class="phrase-icon">“</span><div><b>${escapeHtml(phrase[1])}</b><p>${escapeHtml(phrase[2])}</p><small>${escapeHtml(nextLine)}</small></div></div>`;
    }).join("");
  }

  const learningButton = document.getElementById("learningDone");
  const practiceButton = document.getElementById("practiceDone");
  const practiceDetails = document.getElementById("practiceDetails");
  const toast = document.getElementById("toast");
  let status = { learning: false, practice: false };
  try {
    const saved = JSON.parse(localStorage.getItem("uxdl-day01-status") || "{}");
    status = { learning: saved.learning === true, practice: saved.practice === true };
  } catch (_) { /* Keep the page usable if local browser storage is unavailable. */ }
  let toastTimer;
  function notify(message) {
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2300);
  }
  function syncStatus() {
    learningButton.classList.toggle("is-done", status.learning);
    learningButton.setAttribute("aria-pressed", String(status.learning));
    learningButton.querySelector(".review-text").innerHTML = `<b>Learning Completed</b><small>${status.learning ? "今天的学习已完成 · Saved on this device" : "完成今天的学习内容后标记"}</small>`;
    learningButton.querySelector(".review-check").textContent = status.learning ? "✓" : "○";
    practiceButton.classList.toggle("is-done", status.practice);
    practiceButton.setAttribute("aria-pressed", String(status.practice));
    practiceButton.querySelector(".state-text").textContent = status.practice ? "Practice completed" : "Mark practice complete";
    document.getElementById("practiceStatus").textContent = status.practice ? "COMPLETED" : "IN PROGRESS";
    document.getElementById("practiceStatusIcon").textContent = status.practice ? "✓" : "○";
    document.getElementById("practiceStatusText").textContent = status.practice ? "Day 01 practice marked complete · 已完成" : "完成 Day 01 访谈计划后标记为已完成";
    const completed = Number(status.learning) + Number(status.practice);
    const percent = Math.round(completed / 2 * 100);
    document.getElementById("progressPercent").textContent = `${percent}%`;
    document.getElementById("progressBar").style.width = `${percent}%`;
    document.getElementById("progressCopy").textContent = `Learning ${status.learning ? "✓" : "○"} · Practice ${status.practice ? "✓" : "○"}`;
  }
  function saveStatus() {
    try { localStorage.setItem("uxdl-day01-status", JSON.stringify(status)); } catch (_) { /* Keep in-memory progress for this visit. */ }
    syncStatus();
  }
  learningButton.addEventListener("click", () => {
    status.learning = !status.learning;
    saveStatus();
    notify(status.learning ? "Learning progress saved" : "Learning status reset");
  });
  practiceButton.addEventListener("click", () => {
    status.practice = !status.practice;
    saveStatus();
    notify(status.practice ? "Practice progress saved" : "Practice status reset");
  });
  syncStatus();

  const upcomingDialog = document.getElementById("upcomingDialog");
  document.getElementById("dialogOk").addEventListener("click", () => upcomingDialog.close());
  nav.querySelectorAll("[data-day-index]").forEach((link) => link.addEventListener("click", (event) => {
    const index = Number(link.dataset.dayIndex);
    if (index === 0) { rail.classList.remove("open"); return; }
    event.preventDefault();
    const day = days[index];
    document.getElementById("dialogDay").textContent = `DAY ${day[0]}`;
    document.getElementById("upcomingTitle").textContent = day[1];
    document.getElementById("dialogChinese").textContent = day[2];
    document.getElementById("dialogStatus").textContent = `${day[3].toUpperCase()} · NOT AVAILABLE YET`;
    document.getElementById("dialogCopy").textContent = `This lesson will be generated by the AI Planner on its scheduled learning date. ${day[1]} content is not available yet.`;
    upcomingDialog.showModal();
  }));

  const rail = document.querySelector(".rail");
  const menuToggle = document.getElementById("menuToggle");
  menuToggle.addEventListener("click", () => rail.classList.toggle("open"));
  document.addEventListener("click", (event) => {
    if (rail.classList.contains("open") && !rail.contains(event.target) && event.target !== menuToggle) rail.classList.remove("open");
  });
  const sectionLinks = [...document.querySelectorAll(".section-nav a")];
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) sectionLinks.forEach((link) => link.classList.toggle("active", link.hash === `#${entry.target.id}`));
    }), { rootMargin: "-25% 0px -65% 0px" });
    document.querySelectorAll(".lesson-section").forEach((section) => observer.observe(section));
  }
  document.querySelectorAll("a[href^='#']").forEach((link) => link.addEventListener("click", () => rail.classList.remove("open")));

  fetch(sourceUrl).then((response) => {
    if (!response.ok) throw new Error("Day 01 source unavailable");
    return response.text();
  }).then((markdown) => {
    const goal = extractSection(markdown, "## Research Goal｜研究目标");
    const method = extractSection(markdown, "## Research Method｜研究方法");
    const target = extractSection(markdown, "## Target User｜目标用户");
    document.getElementById("researchSource").innerHTML = renderMarkdown(["## Research Goal｜研究目标", goal, "## Research Method｜研究方法", method, "## Target User｜目标用户", target].join("\n\n"));
    const vocab = parseVocab(markdown);
    document.getElementById("vocabContent").innerHTML = vocab || `<p class="inline-notice">Vocabulary is included in the <a href="${sourceOnGitHub}" target="_blank" rel="noreferrer">Day 01 source</a>.</p>`;
    document.getElementById("phraseContent").innerHTML = renderPhrases(markdown);
    document.getElementById("practiceContent").innerHTML = renderMarkdown(markdown);
  }).catch(() => {
    const message = `<p class="inline-notice">The Day 01 file could not be loaded. Check the local preview server or <a href="${sourceOnGitHub}" target="_blank" rel="noreferrer">view the source on GitHub</a>.</p>`;
    document.getElementById("researchSource").innerHTML = message;
    document.getElementById("practiceContent").innerHTML = message;
    document.getElementById("vocabContent").innerHTML = message;
  });
})();

