"""Build reviewable outreach drafts using only supplied contact data."""
import json
from campaign import load_campaign, validate_campaign


def generate_personalization(company: dict, campaign=None) -> dict:
    campaign = validate_campaign(campaign) if campaign is not None else load_campaign()
    offer = campaign["offer"]
    result = {**company, "best_contact_name": None, "best_contact_email": None,
              "best_contact_title": None, "opener": None,
              "offer": dict(offer), "generation_mode": "template", "requires_review": True}
    if company.get("recommendation") == "Low priority":
        result.update(personalization_status="skipped", reasoning="Low priority account")
        return result
    contact = company.get("best_contact") or {}
    if not isinstance(contact, dict) or not (contact.get("email") or "").strip():
        result.update(personalization_status="skipped", reasoning="No enriched contact email available")
        return result
    name = " ".join(str(contact.get(k) or "").strip() for k in ("first_name", "last_name")).strip()
    company_name = company.get("name") or company.get("domain") or "your team"
    greeting = str(contact.get("first_name") or "").strip()
    opener = f"{greeting + ', ' if greeting else ''}is {offer['problem']} something {company_name} is looking to address?"
    result.update(best_contact_name=name or None,
                  best_contact_email=contact["email"].strip(),
                  best_contact_title=contact.get("position"), opener=opener,
                  personalization_status="draft",
                  reasoning="Uses the scored account's enriched contact; no inferred company events or results.")
    return result


def main():
    with open("data/enriched/scored_companies.json") as f:
        companies = json.load(f)
    results = [generate_personalization(company) for company in companies]
    with open("data/enriched/personalized_companies.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Prepared {len(results)} accounts for review")


if __name__ == "__main__":
    main()
