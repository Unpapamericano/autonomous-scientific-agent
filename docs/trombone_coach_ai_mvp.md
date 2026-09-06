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

## Deployment

GitHub Pages publishes the existing local-first tracker at `/web/trombone/` and
the React Coach build at `/web/trombone-coach/`. The API must be deployed
separately with a persistent database and object storage before public
multi-user use.
