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
  if (sessions.length < 3) return { status: "insufficient", message: "Registra al menos 3 sesiones para estimar una tendencia." };
  const values = sessions.map((row) => row.quality);
  const xs = values.map((_, index) => index);
  const xMean = xs.reduce((a, b) => a + b, 0) / xs.length;
  const yMean = values.reduce((a, b) => a + b, 0) / values.length;
  const denominator = xs.reduce((sum, x) => sum + (x - xMean) ** 2, 0);
  const slope = denominator ? xs.reduce((sum, x, index) => sum + (x - xMean) * (values[index] - yMean), 0) / denominator : 0;
  const predicted = Math.max(1, Math.min(5, yMean + slope * (values.length + 3 - xMean)));
  const direction = slope > 0.04 ? "mejora" : slope < -0.04 ? "descenso" : "estable";
  return { status: "estimated", direction, slope, predictedQuality: predicted, message: `Tendencia ${direction}; calidad estimada en 3 sesiones: ${predicted.toFixed(1)}/5.` };
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
  document.getElementById("confidence").textContent = forecast.status === "estimated" ? (forecast.direction === "mejora" ? "Señal positiva" : "Revisar rutina") : "Need more data";
  const insight = document.getElementById("insights");
  insight.innerHTML = rows.length ? `<div class="insight"><strong>Pronóstico:</strong> ${esc(forecast.message)}</div><div class="insight"><strong>Calidad media:</strong> ${data.averageQuality.toFixed(1)}/5 · <strong>Fatiga media:</strong> ${data.averageFatigue.toFixed(1)}/5</div><div class="insight"><strong>Siguiente mejora:</strong> ${data.averageFatigue > 3.5 ? "reduce intensidad y prioriza recuperación" : data.averageQuality < 3 ? "usa bloques más cortos y objetivos concretos" : "mantén la constancia y cambia el foco gradualmente"}.</div>` : '<div class="empty">Registra tu primera sesión para ver señales de progreso.</div>';
  const volume = rows.map((row) => row.minutes), quality = rows.map((row) => row.quality), fatigue = rows.map((row) => row.fatigue);
  drawChart(document.getElementById("volumeChart"), [volume], ["#3976d7"], Math.max(60, ...volume));
  drawChart(document.getElementById("qualityChart"), [quality, fatigue], ["#3976d7", "#e5a83b"]);
}

function bindApp() {
  ["generate", "log", "clear", "minutes", "focus", "quality", "fatigue", "notes", "search", "level"].forEach(clone);
  document.querySelectorAll("[data-focus]").forEach((button) => { const copy = button.cloneNode(true); button.replaceWith(copy); copy.addEventListener("click", () => { document.getElementById("focus").value = copy.dataset.focus; setStatus(`Foco seleccionado: ${copy.dataset.focus}.`); }); });
  const generate = document.getElementById("generate"), log = document.getElementById("log"), clear = document.getElementById("clear");
  generate.addEventListener("click", () => setStatus("Plan actualizado. Revisa los bloques antes de tocar."));
  log.addEventListener("click", () => {
    try {
      const row = normalizeSession({ minutes: document.getElementById("minutes").value, focus: document.getElementById("focus").value, quality: document.getElementById("quality").value, fatigue: document.getElementById("fatigue").value, notes: document.getElementById("notes").value });
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...getRows(), row])); document.getElementById("notes").value = ""; setStatus("Sesión guardada localmente."); render();
    } catch (error) { setStatus(error.message); }
  });
  clear.addEventListener("click", () => { if (getRows().length && !window.confirm("¿Borrar todas las sesiones guardadas en este navegador?")) return; localStorage.removeItem(STORAGE_KEY); localStorage.removeItem("brassline.practice.v1"); setStatus("Registro borrado."); render(); });
  ["minutes", "focus", "quality", "fatigue"].forEach((id) => document.getElementById(id).addEventListener("input", () => {}));
  document.getElementById("search").addEventListener("input", () => loadCatalog());
  document.getElementById("level").addEventListener("change", () => loadCatalog());
  document.getElementById("export").addEventListener("click", () => { const blob = new Blob([JSON.stringify(getRows(), null, 2)], { type: "application/json" }); const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `brassline-sessions-${new Date().toISOString().slice(0, 10)}.json`; link.click(); URL.revokeObjectURL(link.href); document.getElementById("dataStatus").textContent = "Datos exportados."; });
  document.getElementById("import").addEventListener("click", () => document.getElementById("file").click());
  document.getElementById("file").addEventListener("change", async (event) => { try { const file = event.target.files[0]; if (!file) return; const rows = JSON.parse(await file.text()); const clean = rows.map(normalizeSession); localStorage.setItem(STORAGE_KEY, JSON.stringify(clean)); document.getElementById("dataStatus").textContent = `${clean.length} sesiones importadas.`; render(); } catch (error) { document.getElementById("dataStatus").textContent = `Importación rechazada: ${error.message}`; } });
}

async function loadCatalog() {
  try {
    const response = await fetch("../../../data/trombone_repertoire.json", { cache: "no-store" }); if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    const items = searchRepertoire(await response.json(), document.getElementById("search").value, document.getElementById("level").value);
    document.getElementById("repertoire").innerHTML = items.length ? items.map((item) => `<article class="piece"><h3>${esc(item.title)}</h3><div class="meta">${esc(item.composer)} · ${esc(item.level)}</div><div class="chips">${item.styles.concat(item.skills).map((value) => `<span class="chip">${esc(value)}</span>`).join("")}</div><div class="meta" style="margin-top:9px"><a href="${esc(item.source_url)}" target="_blank" rel="noreferrer">Open source catalog ↗</a></div></article>`).join("") : '<div class="empty">No hay resultados.</div>';
  } catch (error) { document.getElementById("repertoire").innerHTML = `<div class="empty">No se pudo cargar el catálogo.<br><small>${esc(error.message)}</small></div>`; }
}

if (typeof document !== "undefined") {
  bindApp();
  render();
  loadCatalog();
  window.addEventListener("resize", render);
}
