"""Generate three template drafts without fabricated contacts or outcomes."""
import json
from campaign import load_campaign, validate_campaign


def generate_sequence(company: dict) -> dict:
    result = {"domain": company.get("domain"), "name": company.get("name"),
              "score": company.get("score"), "recommendation": company.get("recommendation"),
              "contact": company.get("best_contact_name"),
              "title": company.get("best_contact_title"),
              "email": company.get("best_contact_email"), "sequence": None,
              "generation_mode": "template", "requires_review": True}
    if company.get("recommendation") == "Low priority":
        result.update(status="skipped", reason="Low priority account")
        return result
    contact = company.get("best_contact") or {}
    email = company.get("best_contact_email")
    if (company.get("personalization_status") != "draft" or not email
            or not isinstance(contact, dict)
            or email != contact.get("email", "").strip() or not company.get("opener")):
        result.update(status="skipped", reason="No contact-backed personalization draft available")
        return result
    name = company.get("name") or company.get("domain") or "your team"
    first_name = str(contact.get("first_name") or "").strip()
    greeting = f"Hi {first_name}," if first_name else "Hello,"
    offer = company.get("offer") or load_campaign()["offer"]
    validate_campaign({"buyer_roles": ["sales"], "excluded_roles": [], "offer": offer})
    bodies = [
        f"{greeting}\n\n{company['opener']}\n\n{offer['description']}\n\n{offer['cta']}",
        f"{greeting}\n\nFollowing up on {offer['name']}.\n\n{offer['description']}\n\nIs that a workflow {name} would want to explore?",
        f"{greeting}\n\nI'll close the loop here. If {offer['problem']} becomes a priority, feel free to reply to this note."
    ]
    subjects = [f"{offer['name']} for {name}", f"Re: {offer['name']} for {name}", "Closing the loop"]
    result.update(status="draft", sequence=[
        {"step": i + 1, "type": kind, "subject": subjects[i], "body": bodies[i] + f"\n\n{offer['sender_name']}"}
        for i, kind in enumerate(("intro", "follow_up", "breakup"))])
    return result


def main():
    with open("data/enriched/personalized_companies.json") as f:
        companies = json.load(f)
    results = [generate_sequence(company) for company in companies]
    with open("data/sequences/sequences.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Prepared {len(results)} sequence results for review")


if __name__ == "__main__":
    main()
