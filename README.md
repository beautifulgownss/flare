# GTM Enrichment Pipeline

An end-to-end pipeline that takes a list of company domains, enriches them with real contact data, scores each account for ICP fit, generates personalized outreach openers, produces full 3-step email sequences, and layers in real-time job and news signals for dynamic scoring — all visualized in a live React dashboard.

Built as a 4-project GTM engineering portfolio.

---

## The problem

Sales and marketing teams spend 30-45 minutes per account on manual research — finding the right contact, validating their email, assessing fit, and writing personalized outreach. Static CRM data goes stale fast. At scale, both problems kill pipeline velocity.

This pipeline automates the entire workflow in seconds — and keeps scoring dynamic by layering in live signals.

---

## What it does

1. **Enriches** a CSV of company domains via the Hunter.io API — returning real contacts, titles, and emails per account
2. **Scores** each account 1-10 based on contact seniority and email discoverability signals
3. **Prioritizes** accounts into High / Medium / Low buckets and selects the best contact per account
4. **Generates** a personalized outreach opener for each high-priority account using an LLM
5. **Sequences** each account into a 3-step email sequence — intro, follow-up, and breakup — personalized to the contact and company context
6. **Fetches live signals** — real-time job postings and news via the Serper API — and computes a composite score weighted 70% base / 30% signals
7. **Visualizes** everything in a React dashboard with three views: Account Prioritization, Email Sequences, and Live Signals

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
dashboard/             → React frontend → localhost:3000
```

---

## Tech stack

- **Python** — pipeline orchestration
- **Hunter.io API** — contact and email enrichment
- **Serper API** — real-time Google search for job postings and news signals
- **OpenAI / Claude** — LLM-powered contact selection, opener generation, and sequence writing
- **React** — frontend dashboard with three tabbed views
- **python-dotenv** — environment variable management
- **pandas** — CSV ingestion

---

## Running the pipeline

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
```

**3. Add your target companies**

Edit `data/input/companies.csv`:

```csv
domain
stripe.com
notion.so
your-target.com
```

**4. Run the full pipeline**

```bash
python3 src/enrich.py
python3 src/score.py
python3 src/personalize.py
python3 src/sequence.py
python3 src/signals.py
```

**5. Launch the dashboard**

```bash
cp data/enriched/personalized_companies.json dashboard/public/
cp data/sequences/sequences.json dashboard/public/
cp data/scored_final/companies_final.json dashboard/public/
cd dashboard && npm start
```

Open `localhost:3000`.

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
| Retool | 10/10 | 10/10 | 10.0 | High priority |
| Stripe | 10/10 | 6/10 | 8.8 | High priority |
| Linear | 9/10 | 6/10 | 8.1 | High priority |
| Notion | 5/10 | 8/10 | 5.9 | Medium priority |

**Key insight:** Notion was deprioritized by static scoring due to low contact discoverability. Live signals caught a $500M ARR announcement, active investor activity, and a new AI agent launch — bumping it to Medium priority. Static data tells you who a company is. Live signals tell you why now is the right time to reach out.

### Email sequences

Each high-priority account gets a 3-step sequence:

| Step | Type | Purpose |
|------|------|---------|
| 1 | Intro | Personalized first touch referencing company-specific context |
| 2 | Follow-up | Adds a new insight or angle, doesn't just bump the thread |
| 3 | Breakup | Closes the loop gracefully, leaves the door open |

---

## Key engineering decisions

**Waterfall enrichment thinking** — Hunter.io returns strong contact data but limited firmographics. In a production version this would stack a second API (People Data Labs, Clearbit) to fill missing fields like industry and employee count.

**Contact relevance over seniority** — the scoring logic selects the most relevant contact for a GTM tool, not just the most senior. A Head of AI Research outranks a Director of Finance even if both are the same title tier.

**Composite scoring weights** — base enrichment score is weighted at 70%, live signals at 30%. This reflects that contact data is more reliable than search-derived signals, while still allowing strong signals to meaningfully shift priorities.

**Eval-first personalization** — the LLM prompt is designed to return structured JSON, making output testable and comparable across prompt versions. Next iteration adds a golden eval set to measure opener quality systematically.

**Sequence coherence** — each follow-up email is aware of the previous step's angle, adding new information rather than just restating the opener. This mirrors how a skilled SDR would actually run a sequence.

---

## Roadmap

- [ ] Swap mock LLM responses for live OpenAI/Anthropic API calls
- [ ] Add People Data Labs as a fallback enrichment source for missing firmographics
- [ ] Add a golden eval set to measure and compare opener and sequence quality across prompt versions
- [ ] Add run history, token cost tracking, and pipeline observability — Project 4

---

## Part of a 4-project GTM engineering portfolio

| Project | Description | Status |
|---------|-------------|--------|
| 1. Enrichment Pipeline | Domain → contacts → scored accounts → personalized openers | ✅ Complete |
| 2. Outbound Sequence Generator | Enriched accounts → 3-step personalized email sequences | ✅ Complete |
| 3. Lead Scoring with Live Signals | Real-time job postings + news signals → dynamic ICP scoring | ✅ Complete |
| 4. GTM Ops Dashboard | Unified pipeline UI with run history and observability | 🔜 Next |
