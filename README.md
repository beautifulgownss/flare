# GTM Enrichment Pipeline

An end-to-end pipeline that takes a list of company domains, enriches them with real contact data, scores each account for ICP fit, generates personalized outreach openers, produces full 3-step email sequences, layers in real-time job and news signals for dynamic scoring, logs every run to a database with cost and latency tracking, sends HTML email alerts when scores shift, syncs every account into a real HubSpot CRM, and runs automatically on a schedule in CI — all visualized in a live React dashboard.

Built as a 5-project GTM engineering portfolio.

---

## The problem

Sales and marketing teams spend 30-45 minutes per account on manual research — finding the right contact, validating their email, assessing fit, and writing personalized outreach. Static CRM data goes stale fast. At scale, both problems kill pipeline velocity.

This pipeline automates the entire workflow in seconds — keeps scoring dynamic with live signals — alerts you when accounts worth re-engaging surface — pushes every account straight into the CRM a sales team actually works from — and runs itself every Monday morning.

---

## What it does

1. **Enriches** a CSV of company domains via the Hunter.io API — returning real contacts, titles, and emails per account
2. **Scores** each account 1-10 based on contact seniority and email discoverability signals
3. **Prioritizes** accounts into High / Medium / Low buckets and selects the best contact per account
4. **Generates** a personalized outreach opener for each high-priority account using an LLM
5. **Sequences** each account into a 3-step email sequence — intro, follow-up, and breakup — personalized to the contact and company context
6. **Fetches live signals** — real-time job postings and news via the Serper API — and computes a composite score weighted 70% base / 30% signals
7. **Detects score changes** between runs and sends an HTML email alert when any account shifts by 1.0+ points
8. **Logs every run** to a SQLite database with timestamp, duration, company scores, and estimated token cost
9. **Syncs every scored account into HubSpot** — creating or updating Company records with composite score, recommendation, and best contact as native CRM fields a rep can filter and sort by
10. **Runs on a schedule** via GitHub Actions every Monday at 9am UTC — fully automated
11. **Visualizes** everything in a React dashboard with four views: Account Prioritization, Email Sequences, Live Signals, and Run History

---

## Architecture

```
data/input/companies.csv
        ↓
src/enrich.py          → Hunter.io API → data/enriched/companies.json
        ↓
src/score.py           → ICP scoring logic → data/enriched/scored_companies.json
        ↓
src/personalize.py     → LLM contact selection + opener → data/enriched/personalized_companies.json
        ↓
src/sequence.py        → LLM 3-step email sequences → data/sequences/sequences.json
        ↓
src/signals.py         → Serper API (jobs + news) → data/scored_final/companies_final.json
        ↓
src/hubspot_sync.py    → HubSpot CRM API → upserts Company records by domain
        ↓
src/diff.py            → score change detection + email alert → data/score_diff.json
        ↓
src/tracker.py         → SQLite logging → data/runs.db + data/runs_export.json
        ↓
src/run_pipeline.py    → orchestrates all steps in one command
        ↓
.github/workflows/
└── pipeline.yml       → scheduled CI on GitHub Actions (every Monday 9am UTC)
        ↓
dashboard/             → React frontend → localhost:3000
```

---

## Tech stack

- **Python** — pipeline orchestration
- **Hunter.io API** — contact and email enrichment
- **Serper API** — real-time Google search for job postings and news signals
- **OpenAI / Claude** — LLM-powered contact selection, opener generation, and sequence writing
- **HubSpot API** — CRM sync via Service Key authentication, with custom property schema and domain-based upsert logic
- **SQLite** — lightweight run history and observability database
- **Gmail SMTP** — HTML email alerting on score threshold crossings
- **GitHub Actions** — scheduled CI pipeline with secret management and artifact uploads
- **React** — frontend dashboard with four tabbed views
- **python-dotenv** — environment variable management
- **pandas** — CSV ingestion

---

## Running the pipeline locally

**1. Clone and set up the environment**

```bash
git clone https://github.com/beautifulgownss/gtm-enrichment-pipeline
cd gtm-enrichment-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Add your API keys**

```bash
cp .env.example .env
```

Fill in your keys:

```
HUNTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
HUBSPOT_SERVICE_KEY=your_key_here
ALERT_EMAIL_SENDER=your_gmail@gmail.com
ALERT_EMAIL_PASSWORD=your_16_char_app_password
```

**3. Add your target companies**

Edit `data/input/companies.csv`:

```csv
domain
stripe.com
notion.so
your-target.com
```

**4. (First-time HubSpot setup only) Create custom properties**

```bash
python3 src/hubspot_setup_properties.py
```

This creates the `composite_score`, `gtm_recommendation`, `best_contact_email`, and `best_contact_name` custom fields on the HubSpot Company object. Only needs to run once per HubSpot account.

**5. Run the full pipeline — one command**

```bash
python3 src/run_pipeline.py
```

This runs all pipeline steps in sequence, syncs every account into HubSpot, detects score changes, sends email alerts if thresholds are crossed, logs the run to SQLite, exports run history to JSON, and auto-copies outputs to the dashboard.

**6. Launch the dashboard**

```bash
cd dashboard && npm start
```

Open `localhost:3000`.

---

## CI / Scheduled runs

The pipeline runs automatically every Monday at 9am UTC via GitHub Actions.

To trigger manually: **Actions** → **GTM Pipeline** → **Run workflow**.

Required GitHub secrets:

| Secret | Description |
|--------|-------------|
| `HUNTER_API_KEY` | Hunter.io API key |
| `SERPER_API_KEY` | Serper.dev API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `HUBSPOT_SERVICE_KEY` | HubSpot Service Key (Settings → Integrations → Service Keys) |
| `ALERT_EMAIL_SENDER` | Gmail address to send alerts from |
| `ALERT_EMAIL_PASSWORD` | Gmail App Password (16 characters, no spaces) |

Pipeline outputs are uploaded as artifacts on every run and available for download from the Actions tab.

---

## HubSpot CRM sync

Every pipeline run pushes the final scored accounts into HubSpot as real Company records — not just JSON files sitting in a repo.

**How it works:**
- Authenticates via a HubSpot Service Key (HubSpot's current recommended pattern for system-to-system API access, replacing legacy private apps)
- Searches for an existing Company by domain before writing — creates a new record if none exists, updates the existing one if it does, so repeated runs never create duplicates
- Maps composite score, final recommendation, and best contact (name + email) onto custom Company properties, visible and filterable directly in the HubSpot UI

**Design decision — non-fatal sync:** the HubSpot sync step is wired into `run_pipeline.py` as a non-blocking step. If the CRM sync fails (API hiccup, rate limit, auth issue), the rest of the pipeline — scoring, dashboard updates, run logging — still completes. A flaky third-party API call shouldn't take down the whole pipeline.

---

## Email alerting

When any account's composite score shifts by 1.0+ points between runs, the pipeline sends an HTML alert email with a score change table, run ID, and a link back to the dashboard.

Alerts fire from `diff.py` — which exits with code 1 when thresholds are crossed, causing GitHub Actions to flag the run as requiring attention.

---

## Sample output

### Account prioritization (static scoring)

| Company | Score | Best Contact | Recommendation |
|---------|-------|-------------|----------------|
| Stripe | 10/10 | Kevin Bognar, VP of Sales | High priority |
| Vercel | 10/10 | Gaspar Garcia, Head of AI Research | High priority |
| Retool | 10/10 | David Hsu, CEO | High priority |
| Linear | 9/10 | Casey Bertenthal, Sales Director | High priority |
| Notion | 5/10 | — | Low priority |

### Signal-weighted scoring (composite)

| Company | Base | Signal | Composite | Final |
|---------|------|--------|-----------|-------|
| Vercel | 10/10 | 10/10 | 10.0 | High priority |
| Retool | 10/10 | 7/10 | 9.1 | High priority |
| Linear | 9/10 | 9/10 | 9.0 | High priority |
| Stripe | 10/10 | 6/10 | 8.8 | High priority |
| Notion | 5/10 | 7/10 | 5.6 | Medium priority |

**Key insight:** Notion was deprioritized by static scoring due to low contact discoverability. Live signals caught a $500M ARR announcement, active investor activity, and a new AI agent launch — bumping it to Medium priority. Static data tells you who a company is. Live signals tell you why now is the right time.

### Email sequences

Each high-priority account gets a 3-step sequence:

| Step | Type | Purpose |
|------|------|---------|
| 1 | Intro | Personalized first touch referencing company-specific context |
| 2 | Follow-up | Adds a new insight or angle, doesn't just bump the thread |
| 3 | Breakup | Closes the loop gracefully, leaves the door open |

### Run history

Every pipeline run is logged automatically:

| Field | Description |
|-------|-------------|
| Run ID | Unique timestamped identifier |
| Duration | End-to-end pipeline execution time |
| Companies processed | Account count per run |
| High / Medium / Low | Priority distribution |
| Avg composite score | Mean signal-weighted score across accounts |
| Estimated token cost | Mock pricing at $0.002/company (gpt-4o-mini rate) |
| Score alerts | Accounts with ±1.0+ composite score change vs prior run |

---

## Key engineering decisions

**Single-command orchestration** — `run_pipeline.py` runs every step in sequence, handles errors, logs the run, and auto-copies outputs to the dashboard. No manual file management between steps.

**Waterfall enrichment thinking** — Hunter.io returns strong contact data but limited firmographics. In a production version this would stack a second API (People Data Labs, Clearbit) to fill missing fields like industry and employee count.

**Contact relevance over seniority** — the scoring logic selects the most relevant contact for a GTM tool, not just the most senior. A Head of AI Research outranks a Director of Finance even if both are the same title tier.

**Composite scoring weights** — base enrichment score is weighted at 70%, live signals at 30%. This reflects that contact data is more reliable than search-derived signals, while still allowing strong signals to meaningfully shift priorities.

**Score change alerting** — `diff.py` compares composite scores between runs and exits with code 1 when any account shifts by ±1.0+, causing GitHub Actions to flag the run and triggering an HTML email alert. This surfaces accounts worth re-engaging without manual monitoring.

**CRM sync as a non-fatal step** — `hubspot_sync.py` is wired into the orchestrator but never blocks the rest of the pipeline on failure. Internal scoring and dashboard data are the source of truth; CRM sync is a downstream consumer of that data, not a dependency for it.

**Upsert by domain, not by name** — company names vary in formatting (e.g. "Stripe" vs "Stripe, Inc."), but domains are stable identifiers. Searching HubSpot by domain before writing guarantees the sync stays idempotent across repeated runs.

**Eval-first personalization** — the LLM prompt is designed to return structured JSON, making output testable and comparable across prompt versions. Next iteration adds a golden eval set to measure opener quality systematically.

**Sequence coherence** — each follow-up email is aware of the previous step's angle, adding new information rather than restating the opener. This mirrors how a skilled SDR would actually run a sequence.

**Observable by default** — every run is persisted to SQLite with full per-company score breakdowns. Cost and latency are tracked from day one, not bolted on later.

---

## Roadmap

- [ ] Swap mock LLM responses for live OpenAI/Anthropic API calls
- [ ] Add People Data Labs as a fallback enrichment source for missing firmographics
- [ ] Add a golden eval set to measure and compare opener and sequence quality across prompt versions
- [ ] Add Slack alerting as a second notification channel alongside email
- [ ] Extend HubSpot sync to create associated Contact records, not just Company records

---

## Part of a 5-project GTM engineering portfolio

| Project | Description | Status |
|---------|-------------|--------|
| 1. Enrichment Pipeline | Domain → contacts → scored accounts → personalized openers | ✅ Complete |
| 2. Outbound Sequence Generator | Enriched accounts → 3-step personalized email sequences | ✅ Complete |
| 3. Lead Scoring with Live Signals | Real-time job postings + news signals → dynamic ICP scoring | ✅ Complete |
| 4. GTM Ops Dashboard | Single-command orchestrator, run history, observability, scheduled CI, email alerting | ✅ Complete |
| 5. HubSpot CRM Sync | Scored accounts → real HubSpot Company records via Service Key auth + domain-based upsert | ✅ Complete |
