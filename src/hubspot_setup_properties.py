import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_KEY = os.getenv("HUBSPOT_SERVICE_KEY")
BASE_URL = "https://api.hubapi.com"

PROPERTIES = [
    {
        "name": "composite_score",
        "label": "Composite Score",
        "type": "number",
        "fieldType": "number",
        "groupName": "companyinformation"
    },
    {
        "name": "gtm_recommendation",
        "label": "GTM Recommendation",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation"
    },
    {
        "name": "best_contact_email",
        "label": "Best Contact Email",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation"
    },
    {
        "name": "best_contact_name",
        "label": "Best Contact Name",
        "type": "string",
        "fieldType": "text",
        "groupName": "companyinformation"
    },
]

def create_properties():
    headers = {
        "Authorization": f"Bearer {HUBSPOT_KEY}",
        "Content-Type": "application/json"
    }
    for prop in PROPERTIES:
        url = f"{BASE_URL}/crm/v3/properties/companies"
        response = requests.post(url, headers=headers, json=prop)
        if response.status_code == 201:
            print(f"✅ Created property: {prop['name']}")
        elif response.status_code == 409:
            print(f"⚠️ Already exists: {prop['name']}")
        else:
            print(f"❌ Failed: {prop['name']} - {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    create_properties()
