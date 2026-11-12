"""Fetch hiring and news signals for each account and score their timing (0-10).

Signals only count when they can be tied to the account: the result is hosted
on the company's domain, on an applicant-tracking board under the company's
slug, or names the company's domain. Name-only matches are not trusted, because
common names ("Linear", "Notion") collide with unrelated results.
"""
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from campaign import load_campaign

SERPER_URL = "https://google.serper.dev/search"

ENRICHED_PATH = "data/enriched/companies.json"
SIGNALS_PATH = "data/signals/signals.json"

SIGNAL_CAP = 5  # per source (jobs, news); timing score = jobs + news, 0-10

ATS_HOSTS = (
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "jobs.lever.co",
    "jobs.ashbyhq.com",
    "apply.workable.com",
)

# (terms, points, reason label), checked in order; first matching tier wins per result.
JOB_TIERS = [
    (["vp of sales", "vp sales", "head of sales", "chief revenue", "cro"], 3, "Hiring senior sales leader"),
    (["sales manager", "account executive", "revops", "revenue operations", "sales operations"], 2,
     "Scaling sales team"),
    (["marketing", "growth", "demand gen", "sdr", "bdr", "lifecycle"], 1, "Growing GTM team"),
]
NEWS_TIERS = [
    (["series", "funding", "raised", "raises", "investment"], 3, "Funding signal"),
    (["launch", "expand", "partnership", "acquires", "acquisition"], 2, "Growth signal"),
    (["hire", "hires", "appoints", "new"], 1, "Expansion signal"),
]


def search(query: str, lookback: str) -> list:
    """Google search via Serper. `lookback` is Google's tbs value, e.g. qdr:m3 for 3 months."""
    # Imported here so the scoring functions stay standard-library only for the offline demo.
    from dotenv import load_dotenv

    from http_client import session

    load_dotenv()
    headers = {"X-API-KEY": os.getenv("SERPER_API_KEY"), "Content-Type": "application/json"}
    payload = {"q": query, "num": 10, "tbs": lookback}
    response = session.post(SERPER_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Serper error: {response.status_code}")
        return []
    return [
        {"title": r.get("title"), "snippet": r.get("snippet"), "link": r.get("link")}
        for r in response.json().get("organic", [])
    ]


def domain_slug(domain: str) -> str:
    """'linear.app' -> 'linear'. Used to match ATS URLs like jobs.lever.co/linear."""
    return (domain or "").split(".")[0].lower()


def is_relevant(result: dict, domain: str) -> bool:
    domain = (domain or "").lower()
    if not domain:
        return False
    link = result.get("link") or ""
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    if host == domain or host.endswith("." + domain):
        return True
    if host in ATS_HOSTS:
        first_segment = parsed.path.strip("/").split("/")[0].lower()
        return first_segment == domain_slug(domain)
    text = f"{result.get('title') or ''} {result.get('snippet') or ''}".lower()
    return re.search(rf"\b{re.escape(domain)}\b", text) is not None


def job_query(name: str, domain: str) -> str:
    boards = " OR ".join(f"site:{h}" for h in (domain, *ATS_HOSTS[1:4]))
    return f'"{name}" ({boards}) (sales OR revenue OR marketing OR revops) jobs'


def news_query(name: str, domain: str) -> str:
    return f'"{name}" "{domain}" (funding OR raises OR launches OR expands OR acquires OR appoints)'


def _term_pattern(term: str) -> re.Pattern:
    # Terms must start on a word boundary. Short acronyms ("cro", "sdr", "new")
    # must also end on one, so "across" or "news" don't count as matches.
    suffix = r"\b" if len(term) <= 3 else ""
    return re.compile(rf"\b{re.escape(term)}{suffix}")


def score_results(results: list, tiers: list, fields=("title", "snippet")) -> tuple:
    """Score results against keyword tiers. Returns (capped score, reasons, evidence)."""
    compiled = [([_term_pattern(t) for t in terms], points, label) for terms, points, label in tiers]
    score, reasons, evidence, seen = 0, [], [], set()
    for r in results:
        link = r.get("link")
        if link and link in seen:
            continue
        seen.add(link)
        text = " ".join(str(r.get(f) or "") for f in fields).lower()
        for patterns, points, label in compiled:
            if any(p.search(text) for p in patterns):
                score += points
                reasons.append(f"{label}: {r.get('title')}")
                evidence.append({"label": label, "title": r.get("title"), "link": link})
                break
    return min(score, SIGNAL_CAP), reasons, evidence


def score_job_results(results: list) -> tuple:
    # Job titles carry the signal. Snippets on generic careers pages mention
    # every department, so matching them inflates scores.
    return score_results(results, JOB_TIERS, fields=("title",))


def score_news_results(results: list) -> tuple:
    return score_results(results, NEWS_TIERS)


def evaluate_signals(company: dict, job_results: list, news_results: list) -> dict:
    """Pure scoring step: filter to account-relevant results, then score them."""
    domain = company.get("domain")
    jobs = [r for r in job_results if is_relevant(r, domain)]
    news = [r for r in news_results if is_relevant(r, domain)]
    job_score, job_reasons, job_evidence = score_job_results(jobs)
    news_score, news_reasons, news_evidence = score_news_results(news)
    return {
        "domain": domain,
        "name": company.get("name"),
        "job_score": job_score,
        "job_reasons": job_reasons[:3],
        "news_score": news_score,
        "news_reasons": news_reasons[:3],
        "total_signal_score": job_score + news_score,
        "signal_evidence": (job_evidence + news_evidence)[:6],
        "results_considered": len(job_results) + len(news_results),
        "results_relevant": len(jobs) + len(news),
    }


def fetch_signals(company: dict, lookback: str) -> dict:
    name = company.get("name") or company.get("domain")
    domain = company.get("domain")
    print(f"  Fetching job and news signals for {name}...")
    job_results = search(job_query(name, domain), lookback)
    news_results = search(news_query(name, domain), lookback)
    return {**evaluate_signals(company, job_results, news_results),
            "raw_jobs": job_results, "raw_news": news_results}


def main():
    campaign = load_campaign()
    lookback = campaign["scoring"]["signal_lookback"]
    with open(ENRICHED_PATH) as f:
        companies = json.load(f)

    Path(SIGNALS_PATH).parent.mkdir(parents=True, exist_ok=True)
    results = []
    for company in companies:
        if company.get("error"):
            continue
        signals = fetch_signals(company, lookback)
        print(f"  {signals['name']}: timing {signals['total_signal_score']}/10 "
              f"({signals['results_relevant']}/{signals['results_considered']} results relevant)")
        results.append(signals)

    with open(SIGNALS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. Signals for {len(results)} accounts written to {SIGNALS_PATH}")


if __name__ == "__main__":
    main()
