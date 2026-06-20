import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_KEY = os.getenv("HUBSPOT_SERVICE_KEY")
BASE_URL = "https://api.hubapi.com"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_KEY}",
    "Content-Type": "application/json"
}

DATA_PATH = "data/scored_final/companies_final.json"


def load_accounts():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def find_company_by_domain(domain):
    """Search for an existing company by domain. Returns the company ID or None."""
    url = f"{BASE_URL}/crm/v3/objects/companies/search"
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "domain",
                "operator": "EQ",
                "value": domain
            }]
        }]
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


def build_properties(account):
    best_contact = account.get("best_contact") or {}
    contact_name = f"{best_contact.get('first_name', '')} {best_contact.get('last_name', '')}".strip()

    return {
        "name": account.get("name", ""),
        "domain": account.get("domain", ""),
        "composite_score": account.get("composite_score"),
        "gtm_recommendation": account.get("final_recommendation", ""),
        "best_contact_email": best_contact.get("email", ""),
        "best_contact_name": contact_name
    }


def upsert_company(account):
    domain = account.get("domain")
    properties = build_properties(account)
    existing_id = find_company_by_domain(domain)

    if existing_id:
        url = f"{BASE_URL}/crm/v3/objects/companies/{existing_id}"
        response = requests.patch(url, headers=HEADERS, json={"properties": properties})
        action = "Updated"
    else:
        url = f"{BASE_URL}/crm/v3/objects/companies"
        response = requests.post(url, headers=HEADERS, json={"properties": properties})
        action = "Created"

    if response.status_code in (200, 201):
        print(f"✅ {action}: {account.get('name')} ({domain})")
    else:
        print(f"❌ Failed on {account.get('name')} ({domain}): {response.status_code}")
        print(response.text)


def sync_all():
    accounts = load_accounts()
    print(f"Syncing {len(accounts)} accounts to HubSpot...")
    for account in accounts:
        upsert_company(account)


if __name__ == "__main__":
    sync_all()
