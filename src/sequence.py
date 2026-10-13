"""Generate three template drafts without fabricated contacts or outcomes."""
import json


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
    bodies = [
        f"{greeting}\n\n{company['opener']}\n\nI built a workflow that enriches target accounts, prioritizes contacts, and prepares outreach drafts for review.\n\nWould a short walkthrough be useful?",
        f"{greeting}\n\nFollowing up on the account research workflow. It connects enrichment and account scores to CRM records, so the research can be used in your existing process.\n\nIs that a workflow {name} would want to explore?",
        f"{greeting}\n\nI'll close the loop here. If account research automation becomes relevant, feel free to reply to this note."
    ]
    subjects = [f"Account research workflow for {name}", f"Re: Account research workflow for {name}", "Closing the loop"]
    result.update(status="draft", sequence=[
        {"step": i + 1, "type": kind, "subject": subjects[i], "body": bodies[i]}
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
