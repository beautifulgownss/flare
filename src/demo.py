"""Offline portfolio demo. Standard library only; no integrations are imported."""
import argparse
import html
import json
from pathlib import Path

from campaign import load_campaign
from score import mock_llm_score
from personalize import generate_personalization
from sequence import generate_sequence

ROOT = Path(__file__).resolve().parents[1]


def render_report(accounts, offer):
    escape = lambda value: html.escape(str(value or ""), quote=True)
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
<p><strong>{account['score']}/10</strong> · {escape(account['recommendation'])}</p>
<p>Selected buyer: {escape(contact.get('position')) or 'None'}<br>{escape(contact.get('email'))}</p>
<ul>{reasons}</ul><h3>Outreach drafts</h3>{details}</article>''')
    generated = sum(bool(account["outreach"]["sequence"]) for account in accounts)
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GTM pipeline | Offline demo</title>
<style>
body{margin:0;background:#fff;color:#172324;font-family:Arial,sans-serif;line-height:1.6}
main{max-width:900px;margin:auto;padding:32px 24px}header{border-bottom:3px solid #172324;padding-bottom:24px}
h1{font-size:clamp(28px,5vw,44px);line-height:1.15}h2{margin-bottom:0}article{padding:24px 0;border-bottom:1px solid #bbb}
.domain{margin-top:0;color:#526164}summary{cursor:pointer;padding:12px 0;font-weight:bold}
summary:focus-visible{outline:3px solid #087e8b}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;padding:16px;background:#f2f6f6}
.note{border:1px solid #172324;padding:12px}h3{font-size:18px}
</style></head><body><main><header><p>COURTNEY YI · GTM ENGINEERING</p>
<h1>From accounts to outreach drafts</h1><p class="note">Offline demo. Every company and contact is fictional.
No network requests, CRM sync, email sends, or model calls.</p>''' + f'''
<p>Offer: {escape(offer['name'])}</p><p>{len(accounts)} accounts · {generated} draft sequences · {len(accounts)-generated} skipped</p>
<p>Scores indicate buyer-role availability and contactability, not proven demand or firmographic fit. All drafts require review.</p>
</header>{''.join(rows)}</main></body></html>'''


def run_demo(input_path=None, output_dir=None, campaign_path=None):
    # Explicitly select the bundled config by default; ambient API keys are irrelevant.
    campaign = load_campaign(campaign_path or ROOT / "config" / "campaign.json")
    with open(input_path or ROOT / "demo" / "companies.json") as file:
        companies = json.load(file)
    if not isinstance(companies, list):
        raise ValueError("Demo companies must be a JSON list")
    accounts = []
    for company in companies:
        scored = mock_llm_score(company, campaign)
        personalized = generate_personalization(scored, campaign)
        accounts.append({**personalized, "outreach": generate_sequence(personalized)})
    accounts.sort(key=lambda account: account["score"], reverse=True)
    destination = Path(output_dir or ROOT / "demo" / "output")
    destination.mkdir(parents=True, exist_ok=True)
    payload = {"mode": "offline_demo", "data_source": "fictional_fixtures",
               "requires_review": True, "campaign": campaign, "accounts": accounts}
    (destination / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (destination / "index.html").write_text(render_report(accounts, campaign["offer"]), encoding="utf-8")
    return destination, payload


def main():
    parser = argparse.ArgumentParser(description="Run the GTM demo with no API keys or dependencies")
    parser.add_argument("--input", type=Path, help="JSON fixture file")
    parser.add_argument("--output", type=Path, help="Output directory (default: demo/output)")
    parser.add_argument("--campaign", type=Path, help="Campaign JSON configuration")
    args = parser.parse_args()
    destination, payload = run_demo(args.input, args.output, args.campaign)
    print(f"Offline demo complete: {len(payload['accounts'])} fictional accounts")
    print(f"Open in a browser: {(destination / 'index.html').resolve()}")
    print("Live pipeline data and dashboard files were not modified.")


if __name__ == "__main__":
    main()
