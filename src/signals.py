import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"


def search(query: str) -> list:
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 5}
    response = requests.post(SERPER_URL, headers=headers, json=payload)

    if response.status_code == 200:
        results = response.json().get("organic", [])
        return [
            {
                "title": r.get("title"),
                "snippet": r.get("snippet"),
                "link": r.get("link"),
            }
            for r in results
        ]
    else:
        print(f"Serper error: {response.status_code}")
        return []


def fetch_signals(company: dict) -> dict:
    name = company.get("name")
    domain = company.get("domain")

    print(f"  Fetching job signals for {name}...")
    job_results = search(f"{name} hiring sales marketing operations 2025 2026")

    print(f"  Fetching news signals for {name}...")
    news_results = search(f"{name} funding announcement expansion 2025 2026")

    # Score signals
    job_score = 0
    job_reasons = []

    for r in job_results:
        text = (r.get("title", "") + " " + r.get("snippet", "")).lower()
        if any(t in text for t in ["vp of sales", "head of sales", "chief revenue", "cro"]):
            job_score += 3
            job_reasons.append(f"Hiring senior sales leader: {r.get('title')}")
        elif any(t in text for t in ["sales manager", "account executive", "revops", "revenue operations"]):
            job_score += 2
            job_reasons.append(f"Scaling sales team: {r.get('title')}")
        elif any(t in text for t in ["marketing", "growth", "demand gen", "sdr", "bdr"]):
            job_score += 1
            job_reasons.append(f"Growing GTM team: {r.get('title')}")

    news_score = 0
    news_reasons = []

    for r in news_results:
        text = (r.get("title", "") + " " + r.get("snippet", "")).lower()
        if any(t in text for t in ["series", "funding", "raised", "investment"]):
            news_score += 3
            news_reasons.append(f"Funding signal: {r.get('title')}")
        elif any(t in text for t in ["launch", "expand", "growth", "partnership"]):
            news_score += 2
            news_reasons.append(f"Growth signal: {r.get('title')}")
        elif any(t in text for t in ["hire", "team", "new"]):
            news_score += 1
            news_reasons.append(f"Expansion signal: {r.get('title')}")

    # Cap signal scores
    job_score = min(job_score, 5)
    news_score = min(news_score, 5)
    total_signal_score = job_score + news_score

    return {
        "domain": domain,
        "name": name,
        "job_score": job_score,
        "job_reasons": job_reasons[:3],
        "news_score": news_score,
        "news_reasons": news_reasons[:3],
        "total_signal_score": total_signal_score,
        "raw_jobs": job_results,
        "raw_news": news_results,
    }


def compute_composite_score(base_score: int, signal_score: int) -> dict:
    # Weight: 70% base enrichment score, 30% live signals
    composite = round((base_score * 0.7) + (signal_score * 0.3), 1)
    composite = min(composite, 10)

    return {
        "base_score": base_score,
        "signal_score": signal_score,
        "composite_score": composite,
        "recommendation": (
            "High priority" if composite >= 7
            else "Medium priority" if composite >= 5
            else "Low priority"
        )
    }


def main():
    with open("data/enriched/scored_companies.json", "r") as f:
        companies = json.load(f)

    results = []
    for company in companies:
        print(f"\nFetching signals for {company.get('name')}...")
        signals = fetch_signals(company)

        composite = compute_composite_score(
            base_score=company.get("score", 5),
            signal_score=signals.get("total_signal_score", 0)
        )

        result = {
            **company,
            "job_score": signals["job_score"],
            "job_reasons": signals["job_reasons"],
            "news_score": signals["news_score"],
            "news_reasons": signals["news_reasons"],
            "total_signal_score": signals["total_signal_score"],
            "composite_score": composite["composite_score"],
            "final_recommendation": composite["recommendation"],
        }

        results.append(result)

        # Save raw signals per company
        signal_path = f"data/signals/{company.get('domain').replace('.', '_')}.json"
        with open(signal_path, "w") as f:
            json.dump(signals, f, indent=2)

        print(f"  Base score: {company.get('score')}/10")
        print(f"  Signal score: {signals['total_signal_score']}/10")
        print(f"  Composite: {composite['composite_score']}/10 — {composite['recommendation']}")

    # Sort by composite score
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    output_path = "data/scored_final/companies_final.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Final scores written to {output_path}")
    print("\nFinal priority order:")
    for r in results:
        print(f"  {r['composite_score']}/10 — {r['name']} ({r['final_recommendation']})")


if __name__ == "__main__":
    main()