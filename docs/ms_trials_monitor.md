# Multiple sclerosis clinical-trials monitor

This work-in-progress page demonstrates a practical use case for the
repository: turning a recognized public registry into an understandable,
refreshable scientific activity monitor.

## Generate a current snapshot

```bash
python scripts/generate_ms_trials_page.py
```

This fetches currently active/open MS studies from the public
[ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api) and writes:

```text
visuals/ms_clinical_trials.html
```

Rerunning the script refreshes statuses, last-update dates, sponsors,
locations, and eligibility text from the official registry.

## Run the live local monitor

```bash
python scripts/serve_ms_trials.py
```

Open `http://127.0.0.1:8765`. Each page request queries ClinicalTrials.gov
again, disables browser caching, and renders a fresh snapshot. This is
near-real-time registry refresh, not a guarantee that the source itself has
updated or that recruitment is still available.

## How to interpret it

- “Current” means the study has an active/open registry status at retrieval time.
- Availability, eligibility, recruitment, and location must be confirmed with
  the research team.
- Counts by status, phase, or intervention are descriptive activity summaries.
  They do not establish treatment benefit, causation, or participant suitability.
- The page is an information tool, not medical advice or a recommendation to
  join a study.
