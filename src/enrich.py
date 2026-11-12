"""Enrich a CSV of company domains with Hunter.io contacts."""
import csv
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from http_client import session

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_URL = "https://api.hunter.io/v2/domain-search"

INPUT_PATH = "data/input/companies.csv"
OUTPUT_PATH = "data/enriched/companies.json"


def normalize_domain(value: str) -> str:
    """'https://www.Stripe.com/pricing' -> 'stripe.com'."""
    domain = (value or "").strip().lower()
    domain = re.sub(r"^[a-z]+://", "", domain)
    domain = domain.split("/")[0].split("?")[0].split("#")[0]
    return domain.removeprefix("www.")


def read_domains(path: str = INPUT_PATH) -> list:
    """Read the `domain` column, normalized and de-duplicated in input order."""
    with open(path, newline="") as f:
        domains = [normalize_domain(row.get("domain", "")) for row in csv.DictReader(f)]
    seen, unique = set(), []
    for domain in domains:
        if domain and domain not in seen:
            seen.add(domain)
            unique.append(domain)
    return unique


def parse_contact(email: dict) -> dict:
    """Keep the fields scoring needs, including Hunter's confidence and verification status."""
    verification = email.get("verification") or {}
    return {
        "first_name": email.get("first_name"),
        "last_name": email.get("last_name"),
        "email": email.get("value"),
        "position": email.get("position"),
        "seniority": email.get("seniority"),
        "department": email.get("department"),
        "confidence": email.get("confidence"),
        "verification_status": verification.get("status"),
    }


def enrich_company(domain: str) -> dict:
    params = {"domain": domain, "api_key": HUNTER_API_KEY}
    response = session.get(HUNTER_URL, params=params)
    if response.status_code != 200:
        print(f"Failed for {domain}: {response.status_code}")
        return {"domain": domain, "error": response.status_code}

    data = response.json().get("data", {})
    emails = data.get("emails", [])
    return {
        "domain": domain,
        "name": data.get("organization") or domain,
        "industry": data.get("industry"),
        "location": data.get("country"),
        "employee_count": data.get("headcount"),
        "linkedin_url": data.get("linkedin"),
        "twitter": data.get("twitter"),
        "emails_found": len(emails),
        "top_contacts": [parse_contact(e) for e in emails],
    }


def main():
    results = []
    for domain in read_domains():
        print(f"Enriching {domain}...")
        results.append(enrich_company(domain))

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. {len(results)} companies written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
