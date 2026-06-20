# GTM Enrichment Pipeline

An end-to-end pipeline that takes a list of company domains, enriches them with real contact data, scores each account for ICP fit, generates personalized outreach openers, produces full 3-step email sequences, layers in real-time job and news signals for dynamic scoring, logs every run with cost and latency tracking, sends email alerts when scores shift, syncs every account and contact into a real HubSpot CRM, and runs on a schedule in CI. All of it shows up in a live React dashboard, with sync observability and a small test suite covering the core logic.

Built as a 5-project GTM engineering portfolio.

---

## The problem

Sales and marketing teams spend 30-45 minutes per account on manual research: finding the right contact, validating their email, assessing fit, writing personalized outreach. Static CRM data goes stale fast. At scale, both problems slow pipeline down.

This pipeline automates that research in seconds, keeps scoring dynamic with live signals, alerts you when accounts worth re-engaging surface, pushes every account and contact into the CRM a sales team actually works from (properly linked, not just dumped in), and runs itself every Monday morning.

---

## What it does

1. **Enriches** a CSV of company domains via the Hunter.io API, returning real contacts, titles, and emails per account
2. **Scores** each account 1-10 based on contact seniority and email discoverability signals
3. **Prioritizes** accounts into High / Medium / Low buckets and selects the best contact per account
4. **Generates** a personalized outreach opener for each high-priority account using an LLM
5. **Sequences** each account into a 3-step email sequence (intro, follow-up, breakup) personalized to the contact and company context
6. **Fetches live signals**, real-time job postings and news via the Serper API, and computes a composite score weighted 70% base / 30% signals
7. **Detects score changes** between runs and sends an HTML email alert when any account shifts by 1.0+ points
8. **Logs every run** to a SQLite database with timestamp, duration, company scores, and estimated token cost
9. **Syncs every scored account into HubSpot**, creating or updating Company records with composite score, recommendation, and best contact as fields a rep can actually filter and sort by
10. **Syncs each account's best contact into HubSpot** too, creating or updating a Contact record and associating it to its parent Company
11. **Tracks sync health per run**, logging status, action taken, and duration for every HubSpot sync attempt
12. **Runs on a schedule** via GitHub Actions every Monday at 9am UTC, fully automated
13. **Visualizes** everything in a React dashboard with five views: Account Prioritization, Email Sequences, Live Signals, Run History, HubSpot Sync
14. **Unit tests** the core scoring logic in isolation, no external API needed

---

## Architecture

```
data/input/companies.csv
        ↓
src/enrich.py                  → Hunter.io API → data/enriched/companies.json
        ↓
src/score.py                   → ICP scoring logic → data/enriched/scored_companies.json
        ↓
src/personalize.py             → LLM contact selection + opener → data/enriched/personalized_companies.json
        ↓
src/sequence.py                → LLM 3-step email sequences → data/sequences/sequences.json
        ↓
src/signals.py                 → Serper API (jobs + news) → data/scored_final/companies_final.json
        ↓
src/hubspot_sync.py            → HubSpot CRM API → upserts Company records by domain
                                  writes data/hubspot_sync_status.json
        ↓
src/hubspot_contacts_sync.py   → HubSpot CRM API → upserts Contact records by email
                                  associates each Contact to its Company
        ↓
src/diff.py                    → score change detection + email alert → data/score_diff.json
        ↓
src/tracker.py                 → SQLite logging → data/runs.db + data/runs_export.json
        ↓
src/run_pipeline.py            → orchestrates all steps in one command
        ↓
.github/workflows/
└── pipeline.yml               → scheduled CI on GitHub Actions (every Monday 9am UTC)
        ↓
dashboard/                     → React frontend → localhost:3000

tests/
└── test_score.py              → unit tests for scoring logic, run via pytest
```

---

## Tech stack

- **Python** for pipeline orchestration
- **Hunter.io API** for contact and email enrichment
- **Serper API** for real-time Google search (job postings, news signals)
- **OpenAI / Claude** for LLM-powered contact selection, opener generation, and sequence writing
- **HubSpot API** for CRM sync via Service Key auth, custom property schema, domain-based Company upsert, email-based Contact upsert, and Contact-to-Company associations
- **SQLite** for run history and observability
- **Gmail SMTP** for HTML email alerts on score threshold crossings
- **GitHub Actions** for scheduled CI with secret management and artifact uploads
- **React** for the dashboard, five tabs
- **pytest** for unit testing the core scoring logic
- **python-dotenv** for environment variables
- **pandas** for CSV ingestion

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

**5. Run the full pipeline, one command**

```bash
python3 src/run_pipeline.py
```

This runs every pipeline step in sequence, syncs accounts and contacts into HubSpot with associations, detects score changes, sends email alerts when thresholds are crossed, logs the run to SQLite, exports run history to JSON, and copies outputs into the dashboard automatically.

**6. Launch the dashboard**

```bash
cd dashboard && npm start
```

Open `localhost:3000`.

**7. Run the test suite**

```bash
python -m pytest tests/ -v
```

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

Pipeline outputs are uploaded as artifacts on every run and downloadable from the Actions tab.

---

## HubSpot CRM sync

Every pipeline run pushes the final scored accounts, and their best contact, into HubSpot as real, linked CRM records. Not just JSON files sitting in a repo.

**Companies (`hubspot_sync.py`)**
- Authenticates via a HubSpot Service Key, HubSpot's current recommended pattern for system-to-system API access (replacing legacy private apps)
- Searches for an existing Company by domain before writing. Creates a new record if none exists, updates the existing one if it does, so repeated runs don't create duplicates
- Maps composite score, final recommendation, and best contact (name + email) onto custom Company properties you can see and filter on directly in HubSpot
- Writes a status report (`data/hubspot_sync_status.json`) on every run: per-account success/failure, action taken, duration

**Contacts (`hubspot_contacts_sync.py`)**
- Searches for an existing Contact by email before writing, same idempotent pattern as Companies, just keyed on email instead of domain
- Creates or updates the Contact's name and job title
- Associates the Contact to its parent Company through HubSpot's v4 associations API, so it's an actual relationship in the CRM, not two records that just happen to reference the same company

**Why the sync is non-fatal:** both HubSpot steps run as non-blocking in `run_pipeline.py`. If a sync fails (rate limit, auth hiccup, whatever), the rest of the pipeline still finishes. Scoring and the dashboard shouldn't go down because a third-party API had a bad moment.

**Dashboard visibility:** the "HubSpot Sync" tab shows last sync time, total/succeeded/failed counts, and a row per account with action taken, duration, and status. Pulled straight from the same status file the sync script writes.

---

## Email alerting

When any account's composite score shifts by 1.0+ points between runs, the pipeline sends an HTML alert email with a score change table, run ID, and a link back to the dashboard.

Alerts fire from `diff.py`, which exits with code 1 when thresholds are crossed, flagging the run in GitHub Actions.

---

## Testing

Core scoring logic (`mock_llm_score` in `score.py`) is unit tested in isolation via pytest, no file I/O or external API calls involved.

```bash
python -m pytest tests/ -v
```

**What's covered:**
- Score adjustments per contact seniority tier (CEO/Founder, VP/Director, Head of/Manager/Lead)
- Best-contact selection. Confirms a higher-tier contact wins out even when a lower-tier contact appears earlier in the list
- Email coverage signal, both the bonus for high coverage and the penalty for zero coverage
- Score capping at the 10-point ceiling
- Recommendation threshold boundaries (High / Medium / Low priority)

Started here on purpose. The scoring function is pure logic with no side effects, so it's the cheapest, highest-value place to start a test suite before tackling anything that touches the filesystem or an external API.

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

**Key insight:** Notion got deprioritized by static scoring because of low contact discoverability. Live signals caught a $500M ARR announcement, active investor activity, and a new AI agent launch, bumping it up to Medium priority. Static data tells you who a company is. Live signals tell you why now is the right time.

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

### HubSpot sync status

Every sync attempt is logged automatically:

| Field | Description |
|-------|-------------|
| Last synced | Timestamp of the most recent sync attempt |
| Total / Succeeded / Failed | Per-run sync outcome counts |
| Per-account action | Created vs. updated, with duration in milliseconds |
| Per-account error | Raw HubSpot error response, when a sync fails |

---

## Key engineering decisions

**Single-command orchestration.** `run_pipeline.py` runs every step in sequence, handles errors, logs the run, and copies outputs to the dashboard. No manual file shuffling between steps.

**Waterfall enrichment thinking.** Hunter.io returns strong contact data but limited firmographics. A production version would stack a second API (People Data Labs, Clearbit) to fill gaps like industry and employee count.

**Contact relevance over seniority.** The scoring logic picks the most relevant contact for a GTM tool, not just the most senior one. A Head of AI Research outranks a Director of Finance even at the same title tier.

**Composite scoring weights.** Base enrichment score is weighted 70%, live signals 30%. Contact data is more reliable than search-derived signals, but strong signals can still meaningfully move the needle.

**Score change alerting.** `diff.py` compares composite scores between runs and exits with code 1 when any account shifts ±1.0+, flagging the run in GitHub Actions and firing an email alert. Surfaces accounts worth re-engaging without anyone having to watch for it.

**CRM sync as a non-fatal step.** Both `hubspot_sync.py` and `hubspot_contacts_sync.py` are wired in but never block the rest of the pipeline if they fail. Internal scoring and dashboard data are the source of truth. CRM sync is a downstream consumer of that, not a dependency for it.

**Upsert by stable identifier, not display name.** Company names vary in formatting ("Stripe" vs "Stripe, Inc."), and people's display names aren't unique. Companies get upserted by domain, Contacts by email, both stable and unique, so syncs stay idempotent across repeated runs.

**Real associations, not just co-located records.** The Contacts sync calls HubSpot's associations API to actually link each Contact to its Company. Two records that happen to reference the same domain aren't a CRM relationship. An association is.

**Sync observability as a first-class output.** `hubspot_sync.py` writes a status file on every run, surfaced right in the dashboard. You can see sync health instead of finding out about it when a rep complains a record's missing.

**Eval-first personalization.** The LLM prompt returns structured JSON so output is testable and comparable across prompt versions. Next step is a golden eval set to measure opener quality systematically.

**Sequence coherence.** Each follow-up email is aware of the previous step's angle, adding new information instead of restating the opener. Mirrors how a skilled SDR actually runs a sequence.

**Observable by default.** Every run gets persisted to SQLite with full per-company score breakdowns. Cost and latency tracked from day one, not bolted on after the fact.

**Testing the logic, not the I/O, first.** The scoring function is deliberately separated from file I/O so it can be unit tested without mocking the filesystem. Tests cover tier-based scoring, best-contact selection under list-order edge cases, email coverage signals, score capping, and recommendation thresholds.

---

## Roadmap

- [ ] Swap mock LLM responses for live OpenAI/Anthropic API calls
- [ ] Add People Data Labs as a fallback enrichment source for missing firmographics
- [ ] Add a golden eval set to measure opener and sequence quality across prompt versions
- [ ] Add Slack alerting alongside email
- [ ] Extend unit test coverage to `signals.py` composite scoring math and `diff.py` threshold detection
- [ ] Add integration tests for the HubSpot sync scripts using a mocked API client

---

## Part of a 5-project GTM engineering portfolio

| Project | Description | Status |
|---------|-------------|--------|
| 1. Enrichment Pipeline | Domain → contacts → scored accounts → personalized openers | ✅ Complete |
| 2. Outbound Sequence Generator | Enriched accounts → 3-step personalized email sequences | ✅ Complete |
| 3. Lead Scoring with Live Signals | Real-time job postings + news signals → dynamic ICP scoring | ✅ Complete |
| 4. GTM Ops Dashboard | Single-command orchestrator, run history, observability, scheduled CI, email alerting | ✅ Complete |
| 5. HubSpot CRM Sync | Scored accounts and contacts synced into real, associated HubSpot records via Service Key auth, idempotent upsert, sync observability, and a unit-tested scoring core | ✅ Complete |
