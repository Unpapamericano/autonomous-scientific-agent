import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AudioMetrics, CoachData, EMPTY_DATA, ExerciseCategory, Goal, PracticeSession, summarize, validateData, validateSession } from "./domain";
import { exportData, loadData, saveData } from "./storage";
import { AudioState, MicrophoneEngine } from "./audio";
import "./styles.css";

const categories: ExerciseCategory[] = ["warm-up", "intonation", "range", "articulation", "repertoire", "rhythm", "tone"];
const nav = ["Dashboard", "Practice", "Analysis", "Progress", "Goals", "Repertoire", "Settings"];
const emptyForm = { exercise: "", category: "warm-up" as ExerciseCategory, durationMinutes: "20", bpm: "", difficulty: "3", lowestNote: "", highestNote: "", notes: "", accuracy: "" };

function App() {
  const [tab, setTab] = useState("Dashboard");
  const [data, setData] = useState<CoachData>(EMPTY_DATA);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string>();
  const [goal, setGoal] = useState({ title: "", targetMinutes: "90", period: "weekly" as Goal["period"] });
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("Loading your local workspace…");
  const [audioState, setAudioState] = useState<AudioState>({ status: "idle", message: "Microphone analysis is optional." });
  const engine = useRef<MicrophoneEngine | undefined>(undefined);

  useEffect(() => { loadData().then((value) => { setData(value); setStatus(value.sessions.length ? "Workspace restored from IndexedDB." : "Ready for your first practice session."); }).catch(() => setStatus("Could not load local data. Export a backup before continuing.")); }, []);
  useEffect(() => { engine.current = new MicrophoneEngine(); return () => engine.current?.stop(); }, []);
  useEffect(() => engine.current?.subscribe(setAudioState), []);

  const persist = async (next: CoachData, success = "Saved locally.") => {
    try { await saveData(next); setData(next); setStatus(success); } catch (error) { setStatus(error instanceof Error ? error.message : "Save failed. Your current data is still on screen."); }
  };
  const summary = useMemo(() => summarize(data.sessions), [data.sessions]);
  const filtered = useMemo(() => data.sessions.filter((s) => `${s.exercise} ${s.category} ${s.notes}`.toLowerCase().includes(query.toLowerCase())).sort((a, b) => Date.parse(b.startedAt) - Date.parse(a.startedAt)), [data.sessions, query]);
  const latest = filtered[0];

  const submitSession = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const samples = engine.current?.getMeasurements() || [];
      const audio: AudioMetrics | undefined = samples.length ? {
        durationSeconds: Math.round((engine.current?.getDurationSeconds() || 0) * 10) / 10,
        lowestNote: samples.map((s) => s.midi).sort((a, b) => a - b).map((m) => samples.find((s) => s.midi === m)?.note)[0],
        highestNote: samples.map((s) => s.midi).sort((a, b) => b - a).map((m) => samples.find((s) => s.midi === m)?.note)[0],
        averageCents: Math.round(samples.reduce((sum, s) => sum + Math.abs(s.cents), 0) / samples.length * 10) / 10,
        pitchStability: Math.round(samples.filter((s) => Math.abs(s.cents) <= 25).length / samples.length * 100),
        pitchSamples: samples,
        source: "measured",
      } : undefined;
      const existing = editingId ? data.sessions.find((item) => item.id === editingId) : undefined;
      const session = validateSession({ id: editingId || crypto.randomUUID(), startedAt: existing?.startedAt || new Date().toISOString(), ...form, durationMinutes: Number(form.durationMinutes), bpm: form.bpm ? Number(form.bpm) : undefined, difficulty: Number(form.difficulty), accuracy: form.accuracy ? Number(form.accuracy) : undefined, audio: audio || existing?.audio, source: audio ? "measured" : "user-entered" });
      const sessions = editingId ? data.sessions.map((item) => item.id === editingId ? session : item) : [session, ...data.sessions];
      await persist({ ...data, sessions }, editingId ? "Practice session updated." : "Practice session saved in IndexedDB.");
      setForm(emptyForm); setEditingId(undefined); setTab("Dashboard");
    } catch (error) { setStatus(error instanceof Error ? error.message : "Please check the session fields."); }
  };

  const deleteSession = async (id: string) => { if (!window.confirm("Delete this session? This cannot be undone.")) return; await persist({ ...data, sessions: data.sessions.filter((s) => s.id !== id) }, "Session deleted."); };
  const addGoal = async (event: FormEvent) => { event.preventDefault(); if (!goal.title.trim() || Number(goal.targetMinutes) < 1) { setStatus("Enter a goal and a positive minute target."); return; } const item: Goal = { id: crypto.randomUUID(), title: goal.title.trim(), targetMinutes: Number(goal.targetMinutes), period: goal.period, active: true, createdAt: new Date().toISOString() }; await persist({ ...data, goals: [item, ...data.goals] }, "Goal saved."); setGoal({ ...goal, title: "" }); };
  const removeGoal = async (id: string) => persist({ ...data, goals: data.goals.filter((item) => item.id !== id) }, "Goal removed.");
  const download = () => { const url = URL.createObjectURL(exportData(data)); const anchor = document.createElement("a"); anchor.href = url; anchor.download = `trombone-coach-${new Date().toISOString().slice(0, 10)}.json`; anchor.click(); URL.revokeObjectURL(url); setStatus("Backup exported."); };
  const importFile = async (file?: File) => {
    if (!file) return;
    try {
      const parsed = validateData(JSON.parse(await file.text()));
      if (data.sessions.length || data.goals.length) {
        const confirmed = window.confirm("Importing replaces the current workspace. Export a backup first if you need it. Continue?");
        if (!confirmed) { setStatus("Import cancelled; existing data was preserved."); return; }
      }
      await persist(parsed, "Backup imported and saved.");
    } catch (error) { setStatus(error instanceof Error ? `Import rejected: ${error.message}` : "Import rejected. Existing data was preserved."); }
  };
  const toggleMic = async () => { if (audioState.status === "running") engine.current?.stop(); else await engine.current?.start(); };

  return <div className="app-shell">
    <aside><div className="brand"><span>TC</span><div><b>Trombone Coach <em>AI</em></b><small>Local practice intelligence</small></div></div><nav>{nav.map((item) => <button className={tab === item ? "active" : ""} onClick={() => setTab(item)} key={item}>{item}</button>)}</nav><div className="privacy"><span className="signal-dot" /><b>Evidence-first</b><p>Measured microphone data, your entries, and recommendations are kept distinct.</p></div></aside>
    <main><header><div><span className="eyebrow">Practice / Measure / Improve</span><h1>{tab}</h1></div><span className="user-pill">Guest player · local workspace</span></header><p className="status" role="status">{status}</p>
      {tab === "Dashboard" && <Dashboard summary={summary} sessions={filtered} latest={latest} onNavigate={setTab} />}
      {tab === "Practice" && <section className="panel"><div className="section-kicker">Session tracker</div><h2>Log a focused practice session</h2><form className="session-form" onSubmit={submitSession}>{[["Exercise or repertoire", "exercise", "text"], ["Duration (minutes)", "durationMinutes", "number"], ["BPM / tempo", "bpm", "number"], ["Lowest note", "lowestNote", "text"], ["Highest note", "highestNote", "text"], ["Self-rated accuracy (%)", "accuracy", "number"]].map(([label, key, type]) => <label key={key}>{label}<input type={type} min={type === "number" ? "0" : undefined} value={form[key as keyof typeof form]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></label>)}<label>Category<select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value as ExerciseCategory })}>{categories.map((item) => <option key={item}>{item}</option>)}</select></label><label>Difficulty (1–5)<input type="number" min="1" max="5" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })} /></label><label className="wide">Session notes<textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></label><div className="wide"><button className="primary">Save practice session →</button></div></form></section>}
      {tab === "Analysis" && <Analysis state={audioState} onToggle={toggleMic} samples={engine.current?.getMeasurements() || []} />}
      {tab === "Progress" && <History sessions={filtered} query={query} setQuery={setQuery} onDelete={deleteSession} onEdit={(session) => { setForm({ exercise: session.exercise, category: session.category, durationMinutes: String(session.durationMinutes), bpm: session.bpm ? String(session.bpm) : "", difficulty: String(session.difficulty), lowestNote: session.lowestNote || "", highestNote: session.highestNote || "", notes: session.notes, accuracy: session.accuracy ? String(session.accuracy) : "" }); setEditingId(session.id); setTab("Practice"); }} />}
      {tab === "Goals" && <Goals goals={data.goals} goal={goal} setGoal={setGoal} onAdd={addGoal} onDelete={removeGoal} summary={summary} />}
      {tab === "Repertoire" && <History sessions={filtered.filter((s) => s.category === "repertoire")} query={query} setQuery={setQuery} onDelete={deleteSession} onEdit={(session) => { setForm({ exercise: session.exercise, category: session.category, durationMinutes: String(session.durationMinutes), bpm: session.bpm ? String(session.bpm) : "", difficulty: String(session.difficulty), lowestNote: session.lowestNote || "", highestNote: session.highestNote || "", notes: session.notes, accuracy: session.accuracy ? String(session.accuracy) : "" }); setEditingId(session.id); setTab("Practice"); }} />}
      {tab === "Settings" && <section className="panel"><div className="section-kicker">Durable local data</div><h2>Backup and recovery</h2><p className="muted">Sessions and goals are stored in IndexedDB and survive refresh and browser restart. JSON backups include all structured data and measured pitch samples.</p><div className="actions"><button className="primary" onClick={download}>Export all data</button><label className="secondary">Import JSON<input hidden type="file" accept="application/json,.json" onChange={(e) => importFile(e.target.files?.[0])} /></label></div><p className="warning">No audio blobs are retained by this MVP; only structured measurements are stored. This avoids filling browser storage and prevents implying a recording was saved when it was not.</p></section>}
    </main>
  </div>;
}

function Dashboard({ summary, sessions, latest, onNavigate }: { summary: ReturnType<typeof summarize>; sessions: PracticeSession[]; latest?: PracticeSession; onNavigate: (tab: string) => void }) {
  const chart = sessions.slice().reverse().map((s) => ({ date: new Date(s.startedAt).toLocaleDateString(undefined, { month: "short", day: "numeric" }), minutes: s.durationMinutes, accuracy: s.accuracy ?? s.audio?.pitchStability ?? null }));
  return <><section className="hero-card"><div><span className="eyebrow">Next best action</span><h2>{latest ? `Continue ${latest.category} with one focused ${latest.durationMinutes}-minute block.` : "Log your first practice session."}</h2><button className="primary" onClick={() => onNavigate("Practice")}>Start practice log →</button></div><div className="hero-score"><span>Practice streak</span><strong>{summary.streak}</strong><small>days</small></div></section><section className="metric-grid">{[["Today", `${summary.todayMinutes} min`], ["This week", `${summary.weekMinutes} min`], ["This month", `${summary.monthMinutes} min`], ["Sessions", `${sessions.length}`]].map(([name, value]) => <article className="metric" key={name}><span>{name}</span><b>{value}</b><small>user-entered history</small></article>)}</section><section className="panel"><div className="panel-heading"><div><div className="section-kicker">Progress</div><h2>Practice volume and accuracy</h2></div></div>{chart.length ? <ResponsiveContainer width="100%" height={250}><LineChart data={chart}><XAxis dataKey="date" /><YAxis /><Tooltip /><Line type="monotone" dataKey="minutes" stroke="#b87333" name="Minutes" /><Line type="monotone" dataKey="accuracy" stroke="#1f5b47" name="Accuracy / stability" connectNulls /></LineChart></ResponsiveContainer> : <p className="muted">Your chart will appear after you save sessions.</p>}</section></>;
}

function History({ sessions, query, setQuery, onDelete, onEdit }: { sessions: PracticeSession[]; query: string; setQuery: (value: string) => void; onDelete: (id: string) => void; onEdit: (session: PracticeSession) => void }) {
  return <section className="panel"><div className="panel-heading"><div><div className="section-kicker">History</div><h2>Practice sessions</h2></div><input aria-label="Search sessions" placeholder="Search…" value={query} onChange={(e) => setQuery(e.target.value)} /></div>{sessions.length ? sessions.map((session) => <div className="session-row" key={session.id}><div><b>{session.exercise}</b><small>{new Date(session.startedAt).toLocaleString()} · {session.category} · {session.durationMinutes} min · difficulty {session.difficulty}</small><small>{session.notes || "No notes"}{session.audio ? ` · measured stability ${session.audio.pitchStability}%` : ""}</small></div><span><button className="text-button" onClick={() => onEdit(session)}>Edit</button> <button className="text-button" onClick={() => onDelete(session.id)}>Delete</button></span></div>) : <p className="muted">No matching sessions. Save a practice entry to begin.</p>}</section>;
}

function Analysis({ state, onToggle, samples }: { state: AudioState; onToggle: () => void; samples: ReturnType<MicrophoneEngine["getMeasurements"]> }) {
  const last = samples[samples.length - 1];
  return <section className="panel"><div className="section-kicker">Browser microphone engine</div><h2>Real-time pitch and intonation</h2><p className="muted">The engine uses Web Audio autocorrelation. It reports only stable signals above its confidence threshold; silence and noisy input remain unavailable.</p><button className="primary" onClick={onToggle}>{state.status === "running" ? "Stop microphone" : "Start microphone"}</button><p className={`audio-state ${state.status}`}>{state.message}</p>{last ? <div className="report-grid"><div className="note"><b>{last.note}</b><span>{last.cents >= 0 ? "+" : ""}{last.cents.toFixed(1)} cents</span><small>{(last.frequencyHz).toFixed(1)} Hz · confidence {(last.confidence * 100).toFixed(0)}%</small></div><div className="note"><b>{samples.length}</b><span>reliable samples</span><small>Save a Practice session to persist these measurements.</small></div></div> : <p className="muted">No reliable pitch detected yet.</p>}</section>;
}

function Goals({ goals, goal, setGoal, onAdd, onDelete, summary }: { goals: Goal[]; goal: { title: string; targetMinutes: string; period: Goal["period"] }; setGoal: (value: typeof goal) => void; onAdd: (event: FormEvent) => void; onDelete: (id: string) => void; summary: ReturnType<typeof summarize> }) {
  return <section className="panel"><div className="section-kicker">Personal targets</div><h2>Goals</h2><form className="goal-form" onSubmit={onAdd}><input placeholder="e.g. Build a consistent warm-up" value={goal.title} onChange={(e) => setGoal({ ...goal, title: e.target.value })} /><input type="number" min="1" placeholder="Minutes" value={goal.targetMinutes} onChange={(e) => setGoal({ ...goal, targetMinutes: e.target.value })} /><select value={goal.period} onChange={(e) => setGoal({ ...goal, period: e.target.value as Goal["period"] })}><option>daily</option><option>weekly</option><option>monthly</option></select><button className="primary">Add goal</button></form>{goals.map((item) => <div className="session-row" key={item.id}><div><b>{item.title}</b><small>{item.targetMinutes} minutes · {item.period} · current week {summary.weekMinutes} minutes</small></div><button className="text-button" onClick={() => onDelete(item.id)}>Delete</button></div>)}{!goals.length && <p className="muted">No goals yet.</p>}</section>;
}

createRoot(document.getElementById("root")!).render(<App />);
