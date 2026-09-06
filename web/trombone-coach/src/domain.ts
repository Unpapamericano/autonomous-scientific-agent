export type MetricSource = "measured" | "user-entered" | "ai-generated";
export type ExerciseCategory = "warm-up" | "intonation" | "range" | "articulation" | "repertoire" | "rhythm" | "tone";

export type PitchMeasurement = {
  frequencyHz: number;
  note: string;
  midi: number;
  cents: number;
  confidence: number;
  source: "microphone";
};

export type AudioMetrics = {
  durationSeconds: number;
  lowestNote?: string;
  highestNote?: string;
  averageCents?: number;
  pitchStability?: number;
  pitchSamples: PitchMeasurement[];
  source: MetricSource;
};

export type PracticeSession = {
  id: string;
  startedAt: string;
  durationMinutes: number;
  exercise: string;
  category: ExerciseCategory;
  difficulty: number;
  bpm?: number;
  lowestNote?: string;
  highestNote?: string;
  accuracy?: number;
  notes: string;
  audio?: AudioMetrics;
  source: MetricSource;
};

export type Goal = {
  id: string;
  title: string;
  targetMinutes: number;
  period: "daily" | "weekly" | "monthly";
  active: boolean;
  createdAt: string;
};

export type CoachData = {
  version: 1;
  sessions: PracticeSession[];
  goals: Goal[];
};

export const EMPTY_DATA: CoachData = { version: 1, sessions: [], goals: [] };

export function validateSession(value: unknown): PracticeSession {
  if (!value || typeof value !== "object") throw new Error("Invalid practice session.");
  const row = value as Partial<PracticeSession>;
  const duration = Number(row.durationMinutes);
  const difficulty = Number(row.difficulty);
  if (!Number.isFinite(duration) || duration < 1 || duration > 1440) throw new Error("Duration must be between 1 and 1,440 minutes.");
  if (!row.exercise?.trim() || row.exercise.length > 160) throw new Error("Exercise name is required.");
  if (!["warm-up", "intonation", "range", "articulation", "repertoire", "rhythm", "tone"].includes(row.category || "")) throw new Error("Choose a valid exercise category.");
  if (!Number.isInteger(difficulty) || difficulty < 1 || difficulty > 5) throw new Error("Difficulty must be 1–5.");
  if (row.bpm !== undefined && row.bpm !== null && (!Number.isFinite(Number(row.bpm)) || Number(row.bpm) < 20 || Number(row.bpm) > 300)) throw new Error("BPM must be between 20 and 300.");
  if (!row.startedAt || Number.isNaN(Date.parse(row.startedAt))) throw new Error("Session date is invalid.");
  return {
    id: String(row.id || crypto.randomUUID()),
    startedAt: row.startedAt,
    durationMinutes: duration,
    exercise: row.exercise.trim(),
    category: row.category as ExerciseCategory,
    difficulty,
    bpm: row.bpm === undefined || row.bpm === null ? undefined : Number(row.bpm),
    lowestNote: row.lowestNote?.trim() || undefined,
    highestNote: row.highestNote?.trim() || undefined,
    accuracy: row.accuracy === undefined || row.accuracy === null ? undefined : Math.max(0, Math.min(100, Number(row.accuracy))),
    notes: String(row.notes || "").trim(),
    audio: row.audio,
    source: row.source === "measured" ? "measured" : "user-entered",
  };
}

export function validateData(value: unknown): CoachData {
  if (!value || typeof value !== "object") throw new Error("Data file must contain an object.");
  const input = value as Partial<CoachData>;
  if (!Array.isArray(input.sessions) || !Array.isArray(input.goals)) throw new Error("Data file is missing sessions or goals.");
  return {
    version: 1,
    sessions: input.sessions.map(validateSession),
    goals: input.goals.map((goal) => ({ ...goal, id: String(goal.id || crypto.randomUUID()), targetMinutes: Number(goal.targetMinutes), title: String(goal.title || "Practice goal"), period: goal.period || "weekly", active: Boolean(goal.active), createdAt: String(goal.createdAt || new Date().toISOString()) })),
  };
}

export function summarize(sessions: PracticeSession[]) {
  const now = Date.now();
  const day = 86400000;
  const inWindow = (days: number) => sessions.filter((s) => now - Date.parse(s.startedAt) <= days * day);
  const total = (rows: PracticeSession[]) => rows.reduce((sum, row) => sum + row.durationMinutes, 0);
  const sorted = [...sessions].sort((a, b) => Date.parse(a.startedAt) - Date.parse(b.startedAt));
  return { totalMinutes: total(sessions), todayMinutes: total(inWindow(1)), weekMinutes: total(inWindow(7)), monthMinutes: total(inWindow(30)), sorted, streak: calculateStreak(sessions) };
}

function calculateStreak(sessions: PracticeSession[]) {
  const days = new Set(sessions.map((session) => new Date(session.startedAt).toISOString().slice(0, 10)));
  let count = 0;
  for (let cursor = new Date(); days.has(cursor.toISOString().slice(0, 10)); cursor = new Date(cursor.getTime() - 86400000)) count += 1;
  return count;
}
