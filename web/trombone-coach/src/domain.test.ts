import { describe, expect, it } from "vitest";
import { summarize, validateData, validateSession } from "./domain";

const session = {
  id: "one",
  startedAt: new Date().toISOString(),
  durationMinutes: 30,
  exercise: "Bb long tones",
  category: "intonation",
  difficulty: 3,
  notes: "Relaxed air",
  source: "user-entered",
};

describe("practice data", () => {
  it("validates and normalizes sessions", () => {
    expect(validateSession(session).durationMinutes).toBe(30);
    expect(() => validateSession({ ...session, durationMinutes: 0 })).toThrow();
  });

  it("rejects corrupted imports without returning partial data", () => {
    expect(() => validateData({ sessions: "bad", goals: [] })).toThrow();
    expect(() => validateData({ sessions: [session], goals: [] })).not.toThrow();
  });

  it("calculates practice windows and streaks", () => {
    const result = summarize([validateSession(session)]);
    expect(result.totalMinutes).toBe(30);
    expect(result.todayMinutes).toBe(30);
    expect(result.streak).toBe(1);
  });
});
