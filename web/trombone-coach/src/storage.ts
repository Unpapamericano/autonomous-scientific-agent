import { CoachData, EMPTY_DATA, validateData } from "./domain";

const DB_NAME = "trombone-coach";
const STORE = "workspace";
const KEY = "coach-data";
const SETTINGS_KEY = "trombone-coach.settings.v1";
let writeQueue = Promise.resolve();

function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("IndexedDB is unavailable."));
  });
}

export async function loadData(): Promise<CoachData> {
  if (!("indexedDB" in window)) return readFallback();
  const db = await openDatabase();
  const value = await new Promise<unknown>((resolve, reject) => {
    const request = db.transaction(STORE).objectStore(STORE).get(KEY);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return value ? validateData(value) : EMPTY_DATA;
}

export async function saveData(data: CoachData): Promise<void> {
  const clean = validateData(data);
  const operation = writeQueue.then(async () => {
    if (!("indexedDB" in window)) {
      localStorage.setItem(KEY, JSON.stringify(clean));
      return;
    }
    const db = await openDatabase();
    await new Promise<void>((resolve, reject) => {
      const request = db.transaction(STORE, "readwrite").objectStore(STORE).put(clean, KEY);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
    db.close();
  }).catch((error) => {
    throw new Error(`Could not save your data. Export a backup before continuing. ${String(error)}`);
  });
  writeQueue = operation.catch(() => {});
  return operation;
}

function readFallback(): CoachData {
  try {
    const value = localStorage.getItem(KEY);
    return value ? validateData(JSON.parse(value)) : EMPTY_DATA;
  } catch {
    return EMPTY_DATA;
  }
}

export function saveSettings(settings: Record<string, string>) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export function exportData(data: CoachData): Blob {
  return new Blob([JSON.stringify(validateData(data), null, 2)], { type: "application/json" });
}
