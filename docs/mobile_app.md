# MS Trial Compass mobile app

## What it is

`mobile/` is a responsive Progressive Web App for Android and iOS. It uses
the same ClinicalTrials.gov API source as the Python monitor, but provides a
mobile-first interface with large touch targets, accessible labels, safe
information notices, search, live refresh, and an offline application shell.

It is intentionally a single web codebase:

- **Android:** install from a supported browser using “Add to Home screen” or
  package this directory with Capacitor for Google Play.
- **iOS:** open in Safari and choose “Add to Home Screen” or package it with
  Capacitor for the App Store.

## Run locally

Serve the repository root over HTTP (service workers do not work from
`file://`):

```bash
python -m http.server 8000
```

Open `http://127.0.0.1:8000/mobile/`.

The page fetches active/open studies from the official ClinicalTrials.gov API
when it loads and whenever **Refresh studies** is pressed. The app does not
store personal health information.

## SEO and accessibility

- descriptive title and meta description
- canonical URL and robots directive
- semantic headings, labeled search, and live result announcements
- responsive portrait layout with safe-area support
- keyboard and touch-friendly controls
- source attribution and non-clinical safety language

## Visual direction

The mobile and web monitors share a calm, high-contrast visual language:

- deep navy for trust and navigation
- electric blue for actions and links
- mint for active or positive registry states
- warm amber for caution and evidence boundaries
- generous spacing, rounded cards, subtle elevation, and responsive type

This keeps the interface contemporary without using color as the only signal.
Status text, headings, labels, and source links remain visible for
accessibility and scientific clarity.

## Important limitations

“Active” means active in the registry at retrieval time. It does not guarantee
availability, eligibility, recruitment, safety, or benefit. Users must verify
details with the study team and a qualified clinician. Study counts are
descriptive activity summaries, not causal or effectiveness analyses.

For a native store release, add a Capacitor shell and platform projects only
after choosing app identifiers, signing credentials, privacy policy hosting,
analytics policy, and store compliance requirements.
