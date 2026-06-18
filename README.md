# GTM Enrichment Pipeline

An end-to-end pipeline that takes a list of company domains, enriches them with real contact data, scores each account for ICP fit, and generates personalized outreach openers using an LLM — all outputted to a live React dashboard.

Built as Project 1 of a 4-part GTM engineering portfolio.

---

## The problem

Sales and marketing teams spend 30-45 minutes per account on manual research — finding the right contact, validating their email, assessing fit, and writing a personalized first line. At scale, that time kills pipeline velocity.

This pipeline automates that entire workflow in seconds.

---

## What it does

1. **Enriches** a CSV of company domains via the Hunter.io API — returning real contacts, titles, and emails per account
2. **Scores** each account 1-10 based on contact seniority and email discoverability signals
3. **Prioritizes** accounts into High / Medium / Low buckets and selects the best contact per account
4. **Generates** a personalized outreach opener for each high-priority account using an LLM
5. **Visualizes** everything in a React dashboard with animated score meters and contact cards

---

## Architecture

```
data/input/companies.csv
        ↓
src/enrich.py          → Hunter.io API → data/enriched/companies.json
        ↓
src/score.py           → ICP scoring logic → data/enriched/scored_companies.json
        ↓
src/personalize.py     → LLM personalization → data/enriched/personalized_companies.json
        ↓
dashboard/             → React frontend → localhost:3000
```

---

## Tech stack

- **Python** — pipeline orchestration
- **Hunter.io API** — contact and email enrichment
- **OpenAI / Claude** — LLM-powered contact selection and opener generation
- **React** — frontend dashboard
- **python-dotenv** — environment variable management
- **pandas** — CSV ingestion

---

## Running the pipeline

**1. Clone and set up the environment**

```bash
git clone https://github.com/your-username/gtm-enrichment-pipeline
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
```

**5. Launch the dashboard**

```bash
cp data/enriched/personalized_companies.json dashboard/public/
cd dashboard && npm start
```

Open `localhost:3000`.

---

## Sample output

| Company | Score | Best Contact | Recommendation |
|---------|-------|-------------|----------------|
| Stripe | 10/10 | Kevin Bognar, VP of Sales | High priority |
| Vercel | 10/10 | Gaspar Garcia, Head of AI Research | High priority |
| Retool | 10/10 | David Hsu, CEO | High priority |
| Linear | 9/10 | Casey Bertenthal, Sales Director | High priority |
| Notion | 5/10 | — | Low priority |

---

## Key engineering decisions

**Waterfall enrichment thinking** — Hunter.io returns strong contact data but limited firmographics. In a production version this would stack a second API (People Data Labs, Clearbit) to fill missing fields like industry and employee count.

**Contact relevance over seniority** — the scoring logic selects the most *relevant* contact for a GTM tool, not just the most senior. A Head of AI Research outranks a Director of Finance even if both are the same title tier.

**Eval-first personalization** — the LLM prompt is designed to return structured JSON, making output testable and comparable across prompt versions. Next iteration adds a golden eval set to measure opener quality systematically.

---

## Roadmap

- [ ] Swap mock LLM responses for live OpenAI/Anthropic API calls
- [ ] Add People Data Labs as a fallback enrichment source for missing firmographics
- [ ] Build a CI pipeline that re-scores accounts when new contacts are discovered
- [ ] Add a golden eval set to measure and compare opener quality across prompt versions

---

## Part of a 4-project GTM engineering portfolio

| Project | Description | Status |
|---------|-------------|--------|
| 1. Enrichment Pipeline | Domain → contacts → scored accounts → personalized openers | ✅ Complete |
| 2. Outbound Sequence Generator | Enriched accounts → multi-step email sequences | 🔜 Next |
| 3. Lead Scoring with Live Signals | Real-time job postings + news signals → dynamic ICP scoring | 🔜 Planned |
| 4. GTM Ops Dashboard | Unified pipeline UI with run history and observability | 🔜 Planned |
