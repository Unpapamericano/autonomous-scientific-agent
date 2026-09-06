export const STORAGE_KEY = "brassline.practice.v2";

export function normalizeSession(value) {
  if (!value || typeof value !== "object") throw new Error("Invalid session");
  const minutes = Number(value.minutes);
  const quality = Number(value.quality);
  const fatigue = Number(value.fatigue);
  if (!Number.isFinite(minutes) || minutes < 1 || minutes > 600) throw new Error("Minutes must be between 1 and 600");
  if (!Number.isFinite(quality) || quality < 1 || quality > 5) throw new Error("Quality must be between 1 and 5");
  if (!Number.isFinite(fatigue) || fatigue < 1 || fatigue > 5) throw new Error("Fatigue must be between 1 and 5");
  const date = String(value.date || new Date().toISOString());
  if (Number.isNaN(Date.parse(date))) throw new Error("Invalid session date");
  return {
    id: String(value.id || `${Date.now()}-${Math.random().toString(36).slice(2)}`),
    date, minutes, quality, fatigue,
    focus: String(value.focus || "fundamentals").trim() || "fundamentals",
    notes: String(value.notes || "").trim(),
  };
}

export function transformSessions(rows) {
  const sessions = rows.map(normalizeSession).sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
  const focusMinutes = {};
  for (const session of sessions) focusMinutes[session.focus] = (focusMinutes[session.focus] || 0) + session.minutes;
  return {
    sessions,
    totalMinutes: sessions.reduce((sum, row) => sum + row.minutes, 0),
    averageQuality: sessions.length ? sessions.reduce((sum, row) => sum + row.quality, 0) / sessions.length : 0,
    averageFatigue: sessions.length ? sessions.reduce((sum, row) => sum + row.fatigue, 0) / sessions.length : 0,
    focusMinutes,
  };
}

export function searchRepertoire(catalog, query = "", level = "") {
  const needle = query.trim().toLowerCase();
  return catalog.filter((item) => {
    const haystack = JSON.stringify(item).toLowerCase();
    return (!needle || haystack.includes(needle)) && (!level || item.level.toLowerCase() === level.toLowerCase());
  });
}

export function forecastProgress(rows) {
  const sessions = transformSessions(rows).sessions;
  if (sessions.length < 3) return { status: "insufficient", message: "Log at least 3 sessions to estimate a trend." };
  const values = sessions.map((row) => row.quality);
  const xs = values.map((_, index) => index);
  const xMean = xs.reduce((a, b) => a + b, 0) / xs.length;
  const yMean = values.reduce((a, b) => a + b, 0) / values.length;
  const denominator = xs.reduce((sum, x) => sum + (x - xMean) ** 2, 0);
  const slope = denominator ? xs.reduce((sum, x, index) => sum + (x - xMean) * (values[index] - yMean), 0) / denominator : 0;
  const predicted = Math.max(1, Math.min(5, yMean + slope * (values.length + 3 - xMean)));
  const direction = slope > 0.04 ? "improving" : slope < -0.04 ? "declining" : "steady";
  return { status: "estimated", direction, slope, predictedQuality: predicted, message: `Trend: ${direction}; estimated quality in 3 sessions: ${predicted.toFixed(1)}/5.` };
}

function clone(id) { const node = document.getElementById(id); if (!node) return null; const copy = node.cloneNode(true); node.replaceWith(copy); return copy; }
function esc(value) { const el = document.createElement("span"); el.textContent = value; return el.innerHTML; }
function getRows() {
  try {
    const current = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (Array.isArray(current)) return current;
    const legacy = JSON.parse(localStorage.getItem("brassline.practice.v1") || "[]");
    if (!Array.isArray(legacy)) return [];
    const migrated = legacy.map((row) => normalizeSession({ ...row, quality: row.quality || 3, fatigue: row.fatigue || 2 }));
    localStorage.setItem(STORAGE_KEY, JSON.stringify(migrated));
    return migrated;
  } catch {
    return [];
  }
}
function setStatus(message) { document.getElementById("status").textContent = message; }

function makePlan(minutes, focus) {
  const total = Math.round(minutes);
  const warmup = Math.max(5, Math.round(total * 0.2));
  const technique = Math.max(5, Math.round(total * 0.3));
  const repertoire = Math.max(5, Math.round(total * 0.35));
  const cooldown = total - warmup - technique - repertoire;
  if (cooldown < 5) return null;
  return [
    ["Breathing and long tones", warmup, "Warm up and establish a relaxed sound", "easy"],
    ["Slide technique and articulation", technique, `Develop clean ${focus} coordination`, "moderate"],
    ["Repertoire", repertoire, "Apply the skill to a musical passage", "moderate"],
    ["Cool-down and notes", cooldown, "Record one observation and finish comfortably", "easy"],
  ];
}

function renderPlan(message = "") {
  const minutes = Number(document.getElementById("minutes").value);
  const focus = document.getElementById("focus").value.trim() || "fundamentals";
  const blocks = Number.isFinite(minutes) && minutes >= 20 && minutes <= 240 ? makePlan(minutes, focus) : null;
  const plan = document.getElementById("plan");
  if (!blocks) {
    plan.innerHTML = '<div class="empty">Choose 20–240 minutes for a complete session.</div>';
    setStatus("");
    return false;
  }
  plan.innerHTML = blocks.map(([title, duration, detail, level]) => `<div class="block"><div class="minutes">${duration}<small> min</small></div><div><strong>${esc(title)}</strong><span class="meta">${esc(detail)}</span></div><span class="tag">${esc(level)}</span></div>`).join("");
  setStatus(message);
  return true;
}

function drawChart(canvas, series, colors, max = 5) {
  if (!canvas) return;
  const ratio = window.devicePixelRatio || 1, width = canvas.clientWidth || 500, height = 180;
  canvas.width = width * ratio; canvas.height = height * ratio;
  const ctx = canvas.getContext("2d"); ctx.scale(ratio, ratio); ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#e4e8ef"; ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) { const y = 18 + i * 32; ctx.beginPath(); ctx.moveTo(28, y); ctx.lineTo(width - 8, y); ctx.stroke(); }
  series.forEach((values, index) => {
    if (!values.length) return;
    ctx.strokeStyle = colors[index]; ctx.lineWidth = 3; ctx.beginPath();
    values.forEach((value, point) => { const x = 32 + (width - 45) * (point / Math.max(1, values.length - 1)); const y = 150 - (value / max) * 125; point ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
    ctx.stroke();
  });
}

function render() {
  const rows = getRows(), data = transformSessions(rows), forecast = forecastProgress(rows);
  document.getElementById("sessions").textContent = rows.length;
  document.getElementById("total").textContent = data.totalMinutes;
  const top = Object.entries(data.focusMinutes).sort((a, b) => b[1] - a[1])[0];
  document.getElementById("top").textContent = top ? top[0] : "—";
  document.getElementById("confidence").textContent = forecast.status === "estimated" ? (forecast.direction === "improving" ? "Positive signal" : "Review routine") : "Need more data";
  const insight = document.getElementById("insights");
  insight.innerHTML = rows.length ? `<div class="insight"><strong>Forecast:</strong> ${esc(forecast.message)}</div><div class="insight"><strong>Average quality:</strong> ${data.averageQuality.toFixed(1)}/5 · <strong>Average fatigue:</strong> ${data.averageFatigue.toFixed(1)}/5</div><div class="insight"><strong>Next improvement:</strong> ${data.averageFatigue > 3.5 ? "reduce intensity and prioritize recovery" : data.averageQuality < 3 ? "use shorter blocks and clearer objectives" : "stay consistent and vary your focus gradually"}.</div>` : '<div class="empty">Log your first session to see progress signals.</div>';
  const volume = rows.map((row) => row.minutes), quality = rows.map((row) => row.quality), fatigue = rows.map((row) => row.fatigue);
  drawChart(document.getElementById("volumeChart"), [volume], ["#3976d7"], Math.max(60, ...volume));
  drawChart(document.getElementById("qualityChart"), [quality, fatigue], ["#3976d7", "#e5a83b"]);
}

function bindApp() {
  ["generate", "log", "clear", "minutes", "focus", "quality", "fatigue", "notes", "search", "level", "export", "import", "file"].forEach(clone);
  document.querySelectorAll("[data-focus]").forEach((button) => { const copy = button.cloneNode(true); button.replaceWith(copy); copy.addEventListener("click", () => { document.getElementById("focus").value = copy.dataset.focus; setStatus(`Focus set to ${copy.dataset.focus}.`); }); });
  const generate = document.getElementById("generate"), log = document.getElementById("log"), clear = document.getElementById("clear");
  generate.addEventListener("click", () => renderPlan("Plan updated. Review it before you play."));
  log.addEventListener("click", () => {
    try {
      const row = normalizeSession({ minutes: document.getElementById("minutes").value, focus: document.getElementById("focus").value, quality: document.getElementById("quality").value, fatigue: document.getElementById("fatigue").value, notes: document.getElementById("notes").value });
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...getRows(), row])); document.getElementById("notes").value = ""; setStatus("Session saved locally."); render();
    } catch (error) { setStatus(error.message); }
  });
  clear.addEventListener("click", () => { if (getRows().length && !window.confirm("Delete all practice sessions saved in this browser?")) return; localStorage.removeItem(STORAGE_KEY); localStorage.removeItem("brassline.practice.v1"); setStatus("Practice log cleared."); render(); });
  ["minutes", "focus"].forEach((id) => document.getElementById(id).addEventListener("input", () => renderPlan()));
  document.getElementById("search").addEventListener("input", () => loadCatalog());
  document.getElementById("level").addEventListener("change", () => loadCatalog());
  document.getElementById("export").addEventListener("click", () => { const blob = new Blob([JSON.stringify(getRows(), null, 2)], { type: "application/json" }); const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `brassline-sessions-${new Date().toISOString().slice(0, 10)}.json`; link.click(); URL.revokeObjectURL(link.href); document.getElementById("dataStatus").textContent = "Practice data saved to a JSON file."; });
  document.getElementById("import").addEventListener("click", () => document.getElementById("file").click());
  document.getElementById("file").addEventListener("change", async (event) => { try { const file = event.target.files[0]; if (!file) return; const rows = JSON.parse(await file.text()); if (!Array.isArray(rows)) throw new Error("The file must contain a session list."); const clean = rows.map(normalizeSession); localStorage.setItem(STORAGE_KEY, JSON.stringify(clean)); document.getElementById("dataStatus").textContent = `${clean.length} sessions loaded.`; render(); } catch (error) { document.getElementById("dataStatus").textContent = `Load rejected: ${error.message}`; } });
  renderPlan();
}

async function loadCatalog() {
  try {
    const response = await fetch("../../../data/trombone_repertoire.json", { cache: "no-store" }); if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    const items = searchRepertoire(await response.json(), document.getElementById("search").value, document.getElementById("level").value);
    document.getElementById("repertoire").innerHTML = items.length ? items.map((item) => `<article class="piece"><h3>${esc(item.title)}</h3><div class="meta">${esc(item.composer)} · ${esc(item.level)}</div><div class="chips">${item.styles.concat(item.skills).map((value) => `<span class="chip">${esc(value)}</span>`).join("")}</div><div class="meta" style="margin-top:9px"><a href="${esc(item.source_url)}" target="_blank" rel="noreferrer">Open source catalog ↗</a></div></article>`).join("") : '<div class="empty">No matching repertoire.</div>';
  } catch (error) { document.getElementById("repertoire").innerHTML = `<div class="empty">The repertoire catalog could not load.<br><small>${esc(error.message)}</small></div>`; }
}

if (typeof document !== "undefined") {
  bindApp();
  render();
  loadCatalog();
  window.addEventListener("resize", render);
}
