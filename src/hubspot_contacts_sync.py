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

# HubSpot's standard association type ID for Contact -> Company (primary)
CONTACT_TO_COMPANY_ASSOCIATION_TYPE_ID = 1


def load_accounts():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def find_contact_by_email(email):
    """Search for an existing contact by email. Returns the contact ID or None."""
    url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }]
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


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


def upsert_contact(best_contact):
    email = best_contact.get("email")
    if not email:
        return None

    properties = {
        "email": email,
        "firstname": best_contact.get("first_name", ""),
        "lastname": best_contact.get("last_name", ""),
        "jobtitle": best_contact.get("position", "")
    }

    existing_id = find_contact_by_email(email)

    if existing_id:
        url = f"{BASE_URL}/crm/v3/objects/contacts/{existing_id}"
        response = requests.patch(url, headers=HEADERS, json={"properties": properties})
        action = "Updated"
        contact_id = existing_id
    else:
        url = f"{BASE_URL}/crm/v3/objects/contacts"
        response = requests.post(url, headers=HEADERS, json={"properties": properties})
        action = "Created"
        contact_id = response.json().get("id") if response.status_code == 201 else None

    if response.status_code in (200, 201):
        print(f"  ✅ {action} contact: {properties['firstname']} {properties['lastname']} ({email})")
        return contact_id
    else:
        print(f"  ❌ Failed contact upsert ({email}): {response.status_code}")
        print(f"  {response.text}")
        return None


def associate_contact_to_company(contact_id, company_id):
    """Associate a contact to a company using the v4 associations API."""
    url = f"{BASE_URL}/crm/v4/objects/contacts/{contact_id}/associations/companies/{company_id}"
    payload = [{
        "associationCategory": "HUBSPOT_DEFINED",
        "associationTypeId": CONTACT_TO_COMPANY_ASSOCIATION_TYPE_ID
    }]
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code in (200, 201):
        print(f"  ✅ Associated contact {contact_id} → company {company_id}")
        return True
    else:
        print(f"  ❌ Failed association: {response.status_code}")
        print(f"  {response.text}")
        return False


def sync_all():
    accounts = load_accounts()
    print(f"Syncing contacts for {len(accounts)} accounts to HubSpot...")

    for account in accounts:
        best_contact = account.get("best_contact")
        domain = account.get("domain")
        name = account.get("name")

        if not best_contact or not best_contact.get("email"):
            print(f"⚠️ Skipping {name} — no best contact available")
            continue

        print(f"\n{name} ({domain}):")
        contact_id = upsert_contact(best_contact)
        company_id = find_company_by_domain(domain)

        if contact_id and company_id:
            associate_contact_to_company(contact_id, company_id)
        else:
            print(f"  ⚠️ Skipped association — missing contact_id or company_id")


if __name__ == "__main__":
    sync_all()
