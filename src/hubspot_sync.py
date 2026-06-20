import os
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_KEY = os.getenv("HUBSPOT_SERVICE_KEY")
BASE_URL = "https://api.hubapi.com"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_KEY}",
    "Content-Type": "application/json"
}

DATA_PATH = "data/scored_final/companies_final.json"
STATUS_PATH = "data/hubspot_sync_status.json"


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
    """Upserts a company and returns a status dict for dashboard tracking."""
    domain = account.get("domain")
    name = account.get("name")
    start = time.time()
    properties = build_properties(account)
    existing_id = find_company_by_domain(domain)

    if existing_id:
        url = f"{BASE_URL}/crm/v3/objects/companies/{existing_id}"
        response = requests.patch(url, headers=HEADERS, json={"properties": properties})
        action = "updated"
    else:
        url = f"{BASE_URL}/crm/v3/objects/companies"
        response = requests.post(url, headers=HEADERS, json={"properties": properties})
        action = "created"

    duration_ms = round((time.time() - start) * 1000, 1)

    if response.status_code in (200, 201):
        print(f"✅ {action.capitalize()}: {name} ({domain})")
        return {
            "name": name,
            "domain": domain,
            "status": "success",
            "action": action,
            "hubspot_company_id": response.json().get("id", existing_id),
            "duration_ms": duration_ms,
            "error": None
        }
    else:
        print(f"❌ Failed on {name} ({domain}): {response.status_code}")
        print(response.text)
        return {
            "name": name,
            "domain": domain,
            "status": "failed",
            "action": action,
            "hubspot_company_id": None,
            "duration_ms": duration_ms,
            "error": f"{response.status_code}: {response.text[:200]}"
        }


def sync_all():
    accounts = load_accounts()
    print(f"Syncing {len(accounts)} accounts to HubSpot...")

    results = []
    for account in accounts:
        results.append(upsert_company(account))

    status_report = {
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "succeeded": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "accounts": results
    }

    with open(STATUS_PATH, "w") as f:
        json.dump(status_report, f, indent=2)

    print(f"\nSync status written to {STATUS_PATH}")
    return status_report


if __name__ == "__main__":
    sync_all()
