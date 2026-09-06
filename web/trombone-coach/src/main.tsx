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
  const [file, setFile] = useState<File | null>(null);
  const [recording, setRecording] = useState(false);
  const [message, setMessage] = useState("Upload a WAV recording to begin measured analysis.");
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  const refresh = async () => {
    const response = await fetch(`${API}/api/v1/sessions`);
    if (response.ok) setSessions(await response.json());
  };
  useEffect(() => { refresh().catch(() => setMessage("API unavailable. Start the FastAPI service to analyze audio.")); }, []);

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) { setMessage("Choose a WAV or MP3 file first."); return; }
    const data = new FormData(); data.append("audio", file); data.append("title", "Practice session"); data.append("focus", "intonation");
    setMessage("Analyzing audio...");
    const response = await fetch(`${API}/api/v1/sessions/analyze`, { method: "POST", body: data });
    if (!response.ok) { setMessage((await response.json()).detail || "Analysis failed."); return; }
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
  const nav = ["Dashboard", "Record", "Analysis", "Progress", "Forecast", "Practice", "Exercises", "Repertoire", "Profile", "Settings"];

  return <div className="app-shell">
    <aside><div className="brand"><span>♬</span><div><b>Trombone Coach</b><small>AI practice intelligence</small></div></div>
      <nav>{nav.map((item) => <button className={tab === item ? "active" : ""} onClick={() => setTab(item)} key={item}>{item}</button>)}</nav>
      <div className="privacy"><b>Measured, not imagined</b><p>Every metric includes confidence. AI interpretation never replaces the underlying measurement.</p></div>
    </aside>
    <main><header><div><span className="eyebrow">Practice → Measure → Improve</span><h1>{tab}</h1></div><span className="user-pill">Guest player · Local MVP</span></header>
      {tab === "Record" && <section className="panel"><h2>Record or upload a performance</h2><p className="muted">The current MVP analyzes sustained WAV notes offline. MP3 and advanced pYIN/CREPE analysis are extension points.</p><form onSubmit={analyze}><input type="file" accept=".wav,.mp3,audio/wav,audio/mpeg" onChange={(e) => setFile(e.target.files?.[0] || null)} /><div className="actions"><button type="submit" className="primary">Analyze upload</button><button type="button" onClick={recording ? stopRecording : startRecording} className="secondary">{recording ? "Stop recording" : "Record from microphone"}</button></div></form><p className="status">{message}</p></section>}
      {tab === "Dashboard" && <><section className="hero-card"><div><span className="eyebrow">Your next best action</span><h2>{latest?.recommendations[0] || "Record a sustained note and let the coach measure your baseline."}</h2><p>Confidence-aware feedback for intonation, stability, rhythm, tone, and range.</p><button className="primary" onClick={() => setTab("Record")}>Start a measured session</button></div><div className="hero-score"><strong>{latest?.performance_score.value?.toFixed(0) || "—"}</strong><span>overall score</span></div></section><section className="metric-grid">{[["Intonation", latest && metric(latest.intonation_cents_mean_abs)], ["Stability", latest && metric(latest.pitch_stability)], ["Rhythm", latest && metric(latest.tempo_bpm)], ["Range", latest?.range_low && latest.range_high ? `${latest.range_low}–${latest.range_high}` : "—"]].map(([name, value]) => <article className="metric" key={name}><span>{name}</span><b>{value || "—"}</b><small>Measured in latest session</small></article>)}</section><section className="split"><article className="panel"><h2>Recent sessions</h2>{sessions.length ? sessions.slice(0, 5).map((session) => <div className="session-row" key={session.id}><div><b>{session.title}</b><small>{new Date(session.created_at).toLocaleString()} · {session.filename}</small></div><strong>{session.report.performance_score.value?.toFixed(0) || "—"}</strong></div>) : <p className="muted">No sessions yet.</p>}</article><article className="panel"><h2>Coach interpretation</h2>{latest ? latest.interpretation.map((line) => <p className="callout" key={line}>{line}</p>) : <p className="muted">Your measured interpretation will appear after the first analysis.</p>}</article></section></>}
      {tab === "Analysis" && <section className="panel"><h2>Measured report</h2>{latest ? <><div className="report-grid">{latest.detected_notes.map((note) => <div className="note" key={note.note}><b>{note.note}</b><span>{note.cents_deviation === null ? "Cents withheld" : `${note.cents_deviation > 0 ? "+" : ""}${note.cents_deviation.toFixed(1)} cents`}</span><small>confidence {(note.confidence * 100).toFixed(0)}%</small></div>)}</div>{latest.measured_limitations.map((limit) => <p className="warning" key={limit}>{limit}</p>)}</> : <p className="muted">Run an analysis to see measured note events and limitations.</p>}</section>}
      {["Progress", "Forecast", "Practice", "Exercises", "Repertoire", "Profile", "Settings"].includes(tab) && <section className="panel"><h2>{tab}</h2><p className="muted">This production MVP surface is ready for the next module. Session history, confidence-aware analysis, and the replaceable audio engine are already wired through the API.</p><button className="primary" onClick={() => setTab("Record")}>Create your first measured session</button></section>}
    </main>
  </div>;
}

createRoot(document.getElementById("root")!).render(<App />);
