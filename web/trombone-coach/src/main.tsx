import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import type { FormEvent } from "react";
import "./styles.css";

type Measurement = { value: number | null; unit: string; confidence: number; status: string };
type Report = {
  engine: string; detected_notes: { note: string; cents_deviation: number | null; confidence: number }[];
  intonation_cents_mean_abs: Measurement; pitch_stability: Measurement;
  tempo_bpm: Measurement; performance_score: Measurement; range_low: string | null;
  range_high: string | null; measured_limitations: string[]; interpretation: string[];
  recommendations: string[];
};
type Session = { id: string; title: string; focus: string; filename: string; created_at: string; report: Report };
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const DEMO_SESSIONS: Session[] = [
  { id: "demo-1", title: "Long tones · baseline", focus: "intonation", filename: "demo-baseline.wav", created_at: "2026-09-02T17:20:00Z", report: { engine: "demo", detected_notes: [{ note: "Bb4", cents_deviation: 18, confidence: .94 }], intonation_cents_mean_abs: { value: 18, unit: "cents absolute deviation", confidence: .94, status: "measured" }, pitch_stability: { value: 71, unit: "percent", confidence: .9, status: "measured" }, tempo_bpm: { value: null, unit: "beats per minute", confidence: 0, status: "unavailable" }, performance_score: { value: 68, unit: "score out of 100", confidence: .91, status: "measured" }, range_low: "Bb2", range_high: "Bb4", measured_limitations: ["Demo data is illustrative, not a measurement from your instrument."], interpretation: ["Upper-register pitch is the clearest opportunity in this baseline."], recommendations: ["Practice Bb4–C5 long tones for 5 minutes at 60 BPM."] } },
  { id: "demo-2", title: "Air and connection", focus: "tone", filename: "demo-tone.wav", created_at: "2026-09-03T17:20:00Z", report: { engine: "demo", detected_notes: [{ note: "F4", cents_deviation: 13, confidence: .95 }], intonation_cents_mean_abs: { value: 13, unit: "cents absolute deviation", confidence: .95, status: "measured" }, pitch_stability: { value: 76, unit: "percent", confidence: .92, status: "measured" }, tempo_bpm: { value: null, unit: "beats per minute", confidence: 0, status: "unavailable" }, performance_score: { value: 72, unit: "score out of 100", confidence: .92, status: "measured" }, range_low: "Bb2", range_high: "C5", measured_limitations: [], interpretation: ["Stability is improving while the note center remains slightly sharp."], recommendations: ["Use a slower air attack and sustain each note for 8 seconds."] } },
  { id: "demo-3", title: "Register ladder", focus: "range", filename: "demo-range.wav", created_at: "2026-09-05T17:20:00Z", report: { engine: "demo", detected_notes: [{ note: "C5", cents_deviation: 9, confidence: .97 }], intonation_cents_mean_abs: { value: 9, unit: "cents absolute deviation", confidence: .97, status: "measured" }, pitch_stability: { value: 84, unit: "percent", confidence: .96, status: "measured" }, tempo_bpm: { value: null, unit: "beats per minute", confidence: 0, status: "unavailable" }, performance_score: { value: 81, unit: "score out of 100", confidence: .95, status: "measured" }, range_low: "Bb2", range_high: "D5", measured_limitations: [], interpretation: ["The latest sample shows a more stable upper register."], recommendations: ["Keep the range work at moderate intensity and stop before strain."] } },
];

function metric(measurement: Measurement) {
  return measurement.value === null ? "—" : `${measurement.value.toFixed(1)} ${measurement.unit}`;
}

function encodeWav(buffer: AudioBuffer): Blob {
  const channelCount = Math.min(2, buffer.numberOfChannels);
  const frameCount = buffer.length;
  const dataSize = frameCount * channelCount * 2;
  const output = new ArrayBuffer(44 + dataSize);
  const view = new DataView(output);
  const write = (offset: number, value: string) => [...value].forEach((character, index) => view.setUint8(offset + index, character.charCodeAt(0)));
  write(0, "RIFF"); view.setUint32(4, 36 + dataSize, true); write(8, "WAVE");
  write(12, "fmt "); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, channelCount, true); view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * channelCount * 2, true); view.setUint16(32, channelCount * 2, true);
  view.setUint16(34, 16, true); write(36, "data"); view.setUint32(40, dataSize, true);
  let offset = 44;
  for (let frame = 0; frame < frameCount; frame += 1) {
    for (let channel = 0; channel < channelCount; channel += 1) {
      const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[frame]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true); offset += 2;
    }
  }
  return new Blob([output], { type: "audio/wav" });
}

function App() {
  const [tab, setTab] = useState("Dashboard");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [demoMode, setDemoMode] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [message, setMessage] = useState("Upload a WAV recording to begin measured analysis.");
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  const refresh = async () => {
    const response = await fetch(`${API}/api/v1/sessions`);
    if (!response.ok) throw new Error("API unavailable");
    const records = await response.json();
    setSessions(records.length ? records : DEMO_SESSIONS);
    setDemoMode(!records.length);
  };
  useEffect(() => { refresh().catch(() => { setSessions(DEMO_SESSIONS); setDemoMode(true); setMessage("Demo baseline loaded. Start the API to analyze your own recordings."); }); }, []);

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) { setMessage("Choose a WAV or MP3 file first."); return; }
    const data = new FormData(); data.append("audio", file); data.append("title", "Practice session"); data.append("focus", "intonation");
    setMessage("Analyzing audio...");
    const response = await fetch(`${API}/api/v1/sessions/analyze`, { method: "POST", body: data });
    if (!response.ok) { setMessage((await response.json()).detail || "Analysis failed."); return; }
    setDemoMode(false);
    setMessage("Analysis complete. Measurements are now in your history.");
    await refresh(); setTab("Dashboard");
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunks.current = []; recorder.current = new MediaRecorder(stream);
    recorder.current.ondataavailable = (event) => chunks.current.push(event.data);
    recorder.current.onstop = async () => {
      try {
        const context = new AudioContext();
        const decoded = await context.decodeAudioData(await new Blob(chunks.current, { type: recorder.current?.mimeType }).arrayBuffer());
        setFile(new File([encodeWav(decoded)], "recording.wav", { type: "audio/wav" }));
        await context.close();
        setMessage("Recording ready as WAV. Click Analyze upload to measure it.");
      } catch {
        setMessage("The browser could not convert this recording to WAV. Upload a WAV file instead.");
      } finally {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
    recorder.current.start(); setRecording(true);
  };
  const stopRecording = () => { recorder.current?.stop(); setRecording(false); };
  const latest = sessions[0]?.report;
  const firstScore = sessions[sessions.length - 1]?.report.performance_score.value;
  const latestScore = latest?.performance_score.value;
  const scoreDelta = latestScore !== null && latestScore !== undefined && firstScore !== null && firstScore !== undefined ? latestScore - firstScore : 0;
  const nav = ["Dashboard", "Record", "Analysis", "Progress", "Forecast", "Practice", "Exercises", "Repertoire", "Profile", "Settings"];

  return <div className="app-shell">
    <aside><div className="brand"><span>TC</span><div><b>Trombone Coach <em>AI</em></b><small>Performance intelligence</small></div></div>
      <nav>{nav.map((item) => <button className={tab === item ? "active" : ""} onClick={() => setTab(item)} key={item}>{item}</button>)}</nav>
      <div className="privacy"><span className="signal-dot" /><b>Evidence-first coaching</b><p>Measured signal, confidence, then interpretation. No invented precision.</p></div>
    </aside>
    <main><header><div><span className="eyebrow">Practice / Measure / Improve</span><h1>{tab}</h1></div><div className="header-actions">{demoMode && <span className="demo-pill">Illustrative baseline</span>}<span className="user-pill">Guest player <i>•</i> Local workspace</span></div></header>
      {tab === "Record" && <section className="panel upload-panel"><div className="section-kicker">Capture a clean signal</div><h2>Turn practice into evidence</h2><p className="muted">Use a sustained note or short phrase. The MVP analyzes WAV audio offline and exposes confidence alongside every measured result.</p><form onSubmit={analyze}><label className="file-drop"><input type="file" accept=".wav,.mp3,audio/wav,audio/mpeg" onChange={(e) => setFile(e.target.files?.[0] || null)} /><strong>{file ? file.name : "Drop audio here or choose a file"}</strong><span>WAV recommended · up to 50 MB</span></label><div className="actions"><button type="submit" className="primary">Run analysis <span>→</span></button><button type="button" onClick={recording ? stopRecording : startRecording} className="secondary">{recording ? "Stop recording" : "Record from microphone"}</button></div></form><p className="status">{message}</p></section>}
      {tab === "Dashboard" && <><section className="hero-card"><div><span className="eyebrow">Today’s prescription</span><h2>{latest?.recommendations[0] || "Record a sustained note to establish your performance baseline."}</h2><p>One focused action, grounded in the latest measured signal.</p><button className="primary" onClick={() => setTab("Record")}>Start a measured session <span>→</span></button></div><div className="hero-score"><span>Performance score</span><strong>{latestScore?.toFixed(0) || "—"}</strong><small>{scoreDelta >= 0 ? `+${scoreDelta} since baseline` : `${scoreDelta} since baseline`}</small></div></section><section className="metric-grid">{[["Intonation", latest && metric(latest.intonation_cents_mean_abs), "absolute cents"], ["Stability", latest && metric(latest.pitch_stability), "signal consistency"], ["Tempo", latest && metric(latest.tempo_bpm), "not measured yet"], ["Range", latest?.range_low && latest.range_high ? `${latest.range_low}–${latest.range_high}` : "—", "observed register"]].map(([name, value, detail]) => <article className="metric" key={name}><div className="metric-top"><span>{name}</span><span className="metric-status">● measured</span></div><b>{value || "—"}</b><small>{detail}</small></article>)}</section><section className="dashboard-grid"><article className="panel progress-panel"><div className="panel-heading"><div><div className="section-kicker">Trajectory</div><h2>Performance trend</h2></div><span className="trend-up">↑ {scoreDelta >= 0 ? `${scoreDelta} pts` : `${scoreDelta} pts`}</span></div><div className="sparkline">{sessions.slice().reverse().map((session, index) => <div className="bar" style={{ height: `${Math.max(18, session.report.performance_score.value || 0)}%` }} key={session.id}><span>{session.report.performance_score.value?.toFixed(0)}</span><i /></div>)}</div><div className="chart-axis"><span>Earlier</span><span>Latest</span></div><p className="chart-note">Directional signal from {sessions.length} observations. It is not a guarantee of future performance.</p></article><article className="panel"><div className="section-kicker">Coach readout</div><h2>What to work on next</h2>{latest ? latest.interpretation.map((line) => <p className="callout" key={line}>{line}</p>) : <p className="muted">Your measured interpretation will appear after the first analysis.</p>}<div className="evidence-key"><span><i className="key-dot measured" />Measured</span><span><i className="key-dot interpreted" />Interpreted</span></div></article></section><section className="split"><article className="panel"><div className="panel-heading"><h2>Recent sessions</h2><button className="text-button" onClick={() => setTab("Progress")}>View all →</button></div>{sessions.length ? sessions.slice(0, 5).map((session) => <div className="session-row" key={session.id}><div><b>{session.title}</b><small>{new Date(session.created_at).toLocaleDateString()} · {session.focus}</small></div><strong>{session.report.performance_score.value?.toFixed(0) || "—"}</strong></div>) : <p className="muted">No sessions yet.</p>}</article><article className="panel science-panel"><div className="section-kicker">Method</div><h2>Why this is trustworthy</h2><p>Each result keeps the chain visible: audio signal → measured feature → confidence → coach interpretation.</p><div className="method-row"><b>01</b><span>Measure the signal</span></div><div className="method-row"><b>02</b><span>Flag uncertainty</span></div><div className="method-row"><b>03</b><span>Recommend one action</span></div></article></section></>}
      {tab === "Analysis" && <section className="panel"><h2>Measured report</h2>{latest ? <><div className="report-grid">{latest.detected_notes.map((note) => <div className="note" key={note.note}><b>{note.note}</b><span>{note.cents_deviation === null ? "Cents withheld" : `${note.cents_deviation > 0 ? "+" : ""}${note.cents_deviation.toFixed(1)} cents`}</span><small>confidence {(note.confidence * 100).toFixed(0)}%</small></div>)}</div>{latest.measured_limitations.map((limit) => <p className="warning" key={limit}>{limit}</p>)}</> : <p className="muted">Run an analysis to see measured note events and limitations.</p>}</section>}
      {["Progress", "Forecast", "Practice", "Exercises", "Repertoire", "Profile", "Settings"].includes(tab) && <section className="panel placeholder-panel"><div className="section-kicker">Coming into focus</div><h2>{tab}</h2><p className="muted">This module is designed around the same evidence-first system: measured signal, transparent confidence, and a practical next action. Your current history already powers the foundation.</p><button className="primary" onClick={() => setTab("Record")}>Create a measured session <span>→</span></button></section>}
    </main>
  </div>;
}

createRoot(document.getElementById("root")!).render(<App />);
