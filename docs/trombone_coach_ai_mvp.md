# Trombone Coach AI MVP

Trombone Coach AI is the full-stack successor to the original static practice
tracker. It follows a measurable loop:

**Practice → Measure → Analyze → Diagnose → Recommend → Improve**

## Run the API

Install the project with the web and development dependencies, then start
FastAPI:

```powershell
pip install -e ".[dev,web]"
uvicorn src.trombone_coach.api:app --reload --port 8000
```

The API exposes:

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/sessions`
- `POST /api/v1/sessions/analyze` with a WAV or MP3 multipart upload

The development repository uses SQLite by default at
`data/trombone_coach.db`. The repository boundary is intentionally isolated so
a PostgreSQL/SQLAlchemy implementation can replace it for multi-user
deployments without changing the audio or API contracts.

Set `COACH_JWT_SECRET` for login token issuance. The current UI runs in local
guest mode while the authentication screens are being connected; API
consumers can already register and use bearer tokens.

## Run the React app

```powershell
cd web/trombone-coach
npm install
npm run dev
```

Set `VITE_API_URL` when the API is not running on `http://localhost:8000`.
The app includes Dashboard, Record, Analysis, Progress, Forecast, Practice,
Exercises, Repertoire, Profile, and Settings surfaces. The first release
fully wires Dashboard, Record, Analysis, session history, upload, microphone
capture, and confidence-aware recommendations.

The dashboard opens with a clearly labeled illustrative baseline when no API
history exists. It uses three synthetic observations (68, 72, and 81 score)
to demonstrate the trend layout; these values are never presented as the
player's measurements. Once the API returns a real session, the dashboard
switches to measured history and removes the illustrative state.

## Product style and evidence language

The visual system uses forest green for trust and action, warm brass for
attention and primary calls to action, cream for the instrument-like surface,
and coral only for warnings. Every data surface follows the same hierarchy:

1. **Measured** — a value extracted from the audio signal, with units and
   confidence.
2. **Interpreted** — a plain-language explanation derived from measurements.
3. **Recommended** — one bounded practice action, not a promise of progress.

The interface avoids false precision, separates unavailable metrics from zero,
and labels demo data. This supports a business-grade positioning as a
performance intelligence product rather than a decorative tuner.

## Measurement boundaries

The default `WavAutocorrelationEngine` is a dependency-light baseline for
16-bit PCM WAV. It reports representative sustained-note pitch, cents
deviation when confidence is adequate, pitch stability, range, and an
explainable score. It explicitly marks rhythm, tempo, dynamics, articulation,
vibrato, MIDI alignment, and full tessitura as unavailable until an advanced
engine is selected.

This boundary is deliberate: the product never presents an AI interpretation
as a measured fact and never invents precision when the signal is uncertain.
An optional `audio` extra provides the dependencies needed for a future
librosa/pYIN engine implementing the same `AudioEngine` protocol.

## Governed Coach body

The Coach knowledge layer adopts the useful boundary described by Enoch:
the durable product body is separate from a replaceable runtime or model.
`src/trombone_coach/knowledge.py` contains the versioned mission, principles,
and rulebook adapter. Each report carries an evidence ledger with:

- `measured`: audio-engine output and confidence
- `interpreted`: a rule-based explanation
- `recommended`: a bounded practice action

The ledger is persisted with the session, exposed in the Analysis screen, and
available from `GET /api/v1/coach/body`. This makes future AI providers
replaceable without losing provenance, practice memory, or the ability to
review why a recommendation was made.

## Deployment

GitHub Pages publishes the existing local-first tracker at `/web/trombone/` and
the React Coach build at `/web/trombone-coach/`. The API must be deployed
separately with a persistent database and object storage before public
multi-user use.
