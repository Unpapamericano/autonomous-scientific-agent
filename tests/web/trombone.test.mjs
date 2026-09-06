import test from "node:test";
import assert from "node:assert/strict";
import {
  forecastProgress,
  normalizeSession,
  searchRepertoire,
  transformSessions,
} from "../../web/trombone/app.js";

test("normalizes and rejects invalid practice records", () => {
  const session = normalizeSession({
    date: "2026-09-01",
    minutes: "45",
    quality: "4",
    fatigue: "2",
    focus: "tone",
  });
  assert.equal(session.minutes, 45);
  assert.throws(() => normalizeSession({ minutes: 0, quality: 3, fatigue: 2 }));
});

test("transforms sessions into totals and focus aggregates", () => {
  const result = transformSessions([
    { date: "2026-09-02", minutes: 30, quality: 3, fatigue: 2, focus: "tone" },
    { date: "2026-09-01", minutes: 20, quality: 4, fatigue: 1, focus: "tone" },
    { date: "2026-09-03", minutes: 25, quality: 4, fatigue: 3, focus: "range" },
  ]);
  assert.equal(result.totalMinutes, 75);
  assert.deepEqual(result.focusMinutes, { tone: 50, range: 25 });
  assert.equal(result.sessions[0].date, "2026-09-01");
});

test("searches repertoire by text and level", () => {
  const catalog = [
    { title: "Cavatine", composer: "Saint-Saëns", level: "advanced", skills: ["tone"] },
    { title: "Concerto", composer: "Sachse", level: "intermediate", skills: ["range"] },
  ];
  assert.equal(searchRepertoire(catalog, "tone").length, 1);
  assert.equal(searchRepertoire(catalog, "", "intermediate")[0].title, "Concerto");
});

test("returns a cautious progress forecast after enough sessions", () => {
  const forecast = forecastProgress([
    { date: "2026-09-01", minutes: 30, quality: 2, fatigue: 2, focus: "tone" },
    { date: "2026-09-02", minutes: 30, quality: 3, fatigue: 2, focus: "tone" },
    { date: "2026-09-03", minutes: 30, quality: 4, fatigue: 2, focus: "tone" },
  ]);
  assert.equal(forecast.status, "estimated");
  assert.equal(forecast.direction, "mejora");
  assert.equal(forecast.predictedQuality, 5);
});
