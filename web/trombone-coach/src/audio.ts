import { PitchMeasurement } from "./domain";

export type AudioState = { status: "idle" | "requesting" | "running" | "denied" | "unsupported" | "error"; current?: PitchMeasurement; message: string };
type Listener = (state: AudioState) => void;

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
function frequencyToPitch(frequency: number): PitchMeasurement {
  const midiFloat = 69 + 12 * Math.log2(frequency / 440);
  const midi = Math.round(midiFloat);
  return { frequencyHz: frequency, midi, note: `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`, cents: Math.round((midiFloat - midi) * 1000) / 10, confidence: 0, source: "microphone" };
}

export class MicrophoneEngine {
  private context?: AudioContext;
  private stream?: MediaStream;
  private analyser?: AnalyserNode;
  private frame?: number;
  private listeners = new Set<Listener>();
  private samples: PitchMeasurement[] = [];
  private startedAt = 0;

  subscribe(listener: Listener) {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }
  getMeasurements() { return [...this.samples]; }
  getDurationSeconds() { return this.startedAt ? Math.max(0, (performance.now() - this.startedAt) / 1000) : 0; }
  private emit(state: AudioState) { this.listeners.forEach((listener) => listener(state)); }

  async start() {
    if (!navigator.mediaDevices?.getUserMedia || !window.AudioContext) {
      this.emit({ status: "unsupported", message: "This browser does not provide microphone audio analysis." });
      return;
    }
    try {
      this.emit({ status: "requesting", message: "Requesting microphone permission…" });
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, autoGainControl: false, noiseSuppression: false } });
      this.context = new AudioContext();
      const source = this.context.createMediaStreamSource(this.stream);
      this.analyser = this.context.createAnalyser();
      this.analyser.fftSize = 4096;
      source.connect(this.analyser);
      this.samples = [];
      this.startedAt = performance.now();
      this.emit({ status: "running", message: "Listening. Play a sustained note close to the microphone." });
      this.loop();
    } catch (error) {
      const denied = error instanceof DOMException && ["NotAllowedError", "SecurityError"].includes(error.name);
      this.emit({ status: denied ? "denied" : "error", message: denied ? "Microphone access was denied. You can still log sessions manually." : "Microphone could not be opened." });
    }
  }

  stop() {
    if (this.frame) cancelAnimationFrame(this.frame);
    this.stream?.getTracks().forEach((track) => track.stop());
    this.context?.close();
    this.emit({ status: "idle", message: `Captured ${this.samples.length} reliable pitch samples.` });
  }

  private loop = () => {
    if (!this.analyser || !this.context) return;
    const buffer = new Float32Array(this.analyser.fftSize);
    this.analyser.getFloatTimeDomainData(buffer);
    const pitch = this.detect(buffer, this.context.sampleRate);
    if (pitch) {
      this.samples.push(pitch);
      this.emit({ status: "running", current: pitch, message: `${pitch.note} ${pitch.cents >= 0 ? "+" : ""}${pitch.cents.toFixed(1)} cents · confidence ${(pitch.confidence * 100).toFixed(0)}%` });
    } else this.emit({ status: "running", message: "Listening… confidence is too low for a note." });
    this.frame = requestAnimationFrame(this.loop);
  };

  private detect(buffer: Float32Array, sampleRate: number): PitchMeasurement | undefined {
    const rms = Math.sqrt(buffer.reduce((sum, value) => sum + value * value, 0) / buffer.length);
    if (rms < 0.01) return undefined;
    let bestLag = 0; let best = 0;
    for (let lag = Math.floor(sampleRate / 1000); lag < Math.floor(sampleRate / 50); lag += 1) {
      let correlation = 0;
      for (let i = 0; i < buffer.length - lag; i += 1) correlation += buffer[i] * buffer[i + lag];
      if (correlation > best) { best = correlation; bestLag = lag; }
    }
    const confidence = best / (buffer.reduce((sum, value) => sum + value * value, 0) || 1);
    if (!bestLag || confidence < 0.45) return undefined;
    const result = frequencyToPitch(sampleRate / bestLag);
    result.confidence = Math.min(1, confidence);
    return result.confidence >= 0.65 ? result : undefined;
  };
}
