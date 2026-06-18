import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_URL = "https://api.hunter.io/v2/domain-search"

def enrich_company(domain: str) -> dict:
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
    }
    response = requests.get(HUNTER_URL, params=params)
    
    if response.status_code == 200:
        data = response.json().get("data", {})
        return {
            "domain": domain,
            "name": data.get("organization"),
            "industry": data.get("industry"),
            "location": data.get("country"),
            "employee_count": data.get("employee_count"),
            "linkedin_url": data.get("linkedin"),
            "twitter": data.get("twitter"),
            "emails_found": len(data.get("emails", [])),
            "top_contacts": [
                {
                    "first_name": e.get("first_name"),
                    "last_name": e.get("last_name"),
                    "email": e.get("value"),
                    "position": e.get("position"),
                }
                for e in data.get("emails", [])[:3]
            ]
        }
    else:
        print(f"Failed for {domain}: {response.status_code}")
        return {"domain": domain, "error": response.status_code}

def main():
    df = pd.read_csv("data/input/companies.csv")
    results = []

    for domain in df["domain"]:
        print(f"Enriching {domain}...")
        result = enrich_company(domain)
        results.append(result)

    output_path = "data/enriched/companies.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. {len(results)} companies written to {output_path}")

if __name__ == "__main__":
    main()