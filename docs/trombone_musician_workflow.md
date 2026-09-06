# Trombone musician workflow

This is a musician-focused use case built on the same local-first agent
architecture:

```text
Goal → Research → Practice plan → Record → Review → Refine
```

## Included capabilities

- Generate a bounded practice session with warm-up, slide technique,
  repertoire, and cool-down blocks:

  ```bash
  python scripts/trombone_coach.py --minutes 60 --focus "high register"
  ```

- Filter repertoire metadata by level, style, or skill with
  `src.music.trombone.find_repertoire`.
- Summarize logged practice minutes by focus using
  `src.music.trombone.summarize_practice`.
- Use the web dashboard to record minutes, quality, fatigue, focus, and notes;
  view volume and quality/fatigue charts; search repertoire; and export or
  import the local JSON practice log.
- The progress panel computes descriptive averages and a small linear trend
  forecast after three sessions. It is a planning signal, not a performance
  guarantee or clinical assessment.
- Use the existing adaptive analysis and local model workflows to compare
  recordings, practice notes, method books, and performance goals.

The catalog stores metadata and links only; it does not redistribute
copyrighted sheet music or recordings. Sources should be checked for
copyright, edition, and performance-rights status before use.

## Practice principles

The generated plan is a starting point, not an individualized medical or
pedagogical prescription. Stop or reduce intensity if playing causes pain,
numbness, dizziness, or persistent strain, and consult a qualified teacher or
health professional when appropriate. The cool-down block deliberately records
observations so the next session can adapt to the player's experience.

## Recognized music sources

- [International Trombone Association](https://www.trombone.net/) for
  trombone community, education, and research resources.
- [IMSLP](https://imslp.org/) for edition and public-domain availability
  checks; always verify the specific edition and local law.
- [Library of Congress](https://www.loc.gov/) for public collections and
  catalog metadata.
