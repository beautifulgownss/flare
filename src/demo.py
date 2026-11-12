"""Offline portfolio demo. Standard library only; no integrations are imported."""
import argparse
import html
import json
import tempfile
from pathlib import Path

import tracker
from campaign import load_campaign
from personalize import generate_personalization
from score import score_account
from sequence import generate_sequence
from signals import evaluate_signals

ROOT = Path(__file__).resolve().parents[1]


def render_report(accounts, offer):
    def escape(value):
        return html.escape(str(value or ""), quote=True)

    rows = []
    for account in accounts:
        draft = account["outreach"]
        contact = account.get("best_contact") or {}
        details = "".join(
            f'<details><summary>{escape(step["subject"])}</summary><pre>{escape(step["body"])}</pre></details>'
            for step in draft.get("sequence") or []
        ) or f'<p>{escape(draft.get("reason"))}</p>'
        reasons = "".join(f'<li>{escape(reason)}</li>' for reason in account["reasons"])
        rows.append(f'''<article>
<h2>{escape(account['name'])}</h2><p class="domain">{escape(account['domain'])}</p>
<p><strong>{account['composite_score']}/10</strong> · {escape(account['recommendation'])}
<br>Contactability {account['contactability_score']} · Timing signals {account['total_signal_score']}</p>
<p>Selected buyer: {escape(contact.get('position')) or 'None'}<br>{escape(contact.get('email'))}</p>
<ul>{reasons}</ul><h3>Outreach drafts</h3>{details}</article>''')
    generated = sum(bool(account["outreach"]["sequence"]) for account in accounts)
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flare | Offline demo</title>
<style>
body{margin:0;background:#fff;color:#172324;font-family:Arial,sans-serif;line-height:1.6}
main{max-width:900px;margin:auto;padding:32px 24px}header{border-bottom:3px solid #172324;padding-bottom:24px}
h1{font-size:clamp(28px,5vw,44px);line-height:1.15}h2{margin-bottom:0}article{padding:24px 0;border-bottom:1px solid #bbb}
.domain{margin-top:0;color:#526164}summary{cursor:pointer;padding:12px 0;font-weight:bold}
summary:focus-visible{outline:3px solid #087e8b}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;padding:16px;background:#f2f6f6}
.note{border:1px solid #172324;padding:12px}h3{font-size:18px}
</style></head><body><main><header><p>FLARE · COURTNEY YI</p>
<h1>From accounts to outreach drafts</h1><p class="note">Offline demo. Every company and contact is fictional.
No network requests, CRM sync, email sends, or model calls.</p>''' + f'''
<p>Offer: {escape(offer['name'])}</p><p>{len(accounts)} accounts · {generated} draft sequences · {len(accounts)-generated} skipped</p>
<p>Scores combine buyer contactability with account-specific hiring and news signals. They are not proven demand or firmographic fit. All drafts require review.</p>
</header>{''.join(rows)}</main></body></html>'''


def score_companies(companies, campaign, drop_news_for=()):
    """Run fixtures through the live signal filter, scoring, and draft steps."""
    accounts = []
    for company in companies:
        # Fixture search results go through the same relevance filter and scoring as live runs.
        fixtures = company.get("demo_search_results") or {}
        account = {k: v for k, v in company.items() if k != "demo_search_results"}
        news = [] if account["domain"] in drop_news_for else fixtures.get("news", [])
        signals = evaluate_signals(account, fixtures.get("jobs", []), news)
        scored = score_account(account, signals, campaign)
        personalized = generate_personalization(scored, campaign)
        accounts.append({**personalized, "outreach": generate_sequence(personalized)})
    accounts.sort(key=lambda account: (account["composite_score"], account["domain"]), reverse=True)
    return accounts


def write_dashboard_fixtures(companies, campaign, destination):
    """Fill the dashboard with fictional data: the current run plus a prior run.

    The prior run is the same fixtures before Harbor's funding news appeared, so
    Run History shows a real score change. Nothing here comes from live APIs.
    """
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    current = score_companies(companies, campaign)
    previous = score_companies(companies, campaign, drop_news_for={"harbor-workflows.example"})
    final = [{k: v for k, v in a.items() if k != "outreach"} for a in current]
    files = {
        "companies_final.json": final,
        "personalized_companies.json": final,
        "sequences.json": [a["outreach"] for a in current],
    }
    with tempfile.TemporaryDirectory() as tmp:
        original_db = tracker.DB_PATH
        tracker.DB_PATH = str(Path(tmp) / "runs.db")
        try:
            tracker.init_db()
            tracker.log_run("demo_week_1", previous, 41.2, notes="Fictional demo run")
            tracker.log_run("demo_week_2", final, 43.8, notes="Fictional demo run")
            runs = tracker.get_runs()
            for run in runs:
                run["scores"] = tracker.get_run_scores(run["run_id"])
        finally:
            tracker.DB_PATH = original_db
    # Fixed timestamps keep the fixtures stable between regenerations.
    stamps = {"demo_week_1": "2026-11-02T09:00:00", "demo_week_2": "2026-11-09T09:00:00"}
    for run in runs:
        run["timestamp"] = stamps[run["run_id"]]
    files["runs_export.json"] = sorted(runs, key=lambda r: r["timestamp"], reverse=True)
    for name, payload in files.items():
        (destination / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def run_demo(input_path=None, output_dir=None, campaign_path=None):
    # Explicitly select the bundled config by default; ambient API keys are irrelevant.
    campaign = load_campaign(campaign_path or ROOT / "config" / "campaign.json")
    with open(input_path or ROOT / "demo" / "companies.json") as file:
        companies = json.load(file)
    if not isinstance(companies, list):
        raise ValueError("Demo companies must be a JSON list")
    accounts = score_companies(companies, campaign)
    destination = Path(output_dir or ROOT / "demo" / "output")
    destination.mkdir(parents=True, exist_ok=True)
    payload = {"mode": "offline_demo", "data_source": "fictional_fixtures",
               "requires_review": True, "campaign": campaign, "accounts": accounts}
    (destination / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (destination / "index.html").write_text(render_report(accounts, campaign["offer"]), encoding="utf-8")
    return destination, payload


def main():
    parser = argparse.ArgumentParser(description="Run the Flare demo with no API keys or dependencies")
    parser.add_argument("--input", type=Path, help="JSON fixture file")
    parser.add_argument("--output", type=Path, help="Output directory (default: demo/output)")
    parser.add_argument("--campaign", type=Path, help="Campaign JSON configuration")
    parser.add_argument("--dashboard", action="store_true",
                        help="Also load the fictional data into dashboard/public so `npm start` shows it")
    args = parser.parse_args()
    destination, payload = run_demo(args.input, args.output, args.campaign)
    if args.dashboard:
        with open(args.input or ROOT / "demo" / "companies.json") as file:
            companies = json.load(file)
        target = write_dashboard_fixtures(companies, payload["campaign"], ROOT / "dashboard" / "public")
        print(f"Dashboard loaded with fictional data: {target}. Run `cd dashboard && npm start`.")
    print(f"Offline demo complete: {len(payload['accounts'])} fictional accounts")
    print(f"Open in a browser: {(destination / 'index.html').resolve()}")
    if not args.dashboard:
        print("Live pipeline data and dashboard files were not modified.")


if __name__ == "__main__":
    main()
