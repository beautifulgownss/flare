# GTM Pipeline Dashboard

React front end for the GTM Enrichment Pipeline. It reads the JSON files that
`src/run_pipeline.py` copies into `public/` and renders six views:

| Tab | Data file |
|-----|-----------|
| Account prioritization | `personalized_companies.json` |
| Email sequences | `sequences.json` |
| Live signals | `companies_final.json` |
| Run history | `runs_export.json` |
| HubSpot sync | `hubspot_sync_status.json` |
| Pitch pages | `pitch_pages_status.json` + `pages/*.html` |

Styling uses the in-repo Hockney design system (`src/hockney/`, see `BRAND.md`).

## Commands

```bash
npm install
npm start                          # dev server on http://localhost:3000
CI=true npm test -- --watchAll=false
npm run build                      # production build in build/
```

The checked-in `public/*.json` files are sample output, so the dashboard runs
without running the pipeline first.
