"""Build reviewable outreach drafts using only supplied contact and signal data."""
import json

from campaign import load_campaign, validate_campaign

INPUT_PATH = "data/scored_final/companies_final.json"
OUTPUT_PATH = "data/enriched/personalized_companies.json"

# Signal labels from signals.py -> wording safe to use in an opener. The phrases
# describe the category of evidence, never the raw search-result title.
SIGNAL_PHRASES = {
    "Hiring senior sales leader": "hiring senior sales leadership",
    "Scaling sales team": "growing the sales and revenue team",
    "Growing GTM team": "growing the go-to-market team",
    "Funding signal": "coming off recent funding news",
    "Growth signal": "in the middle of a launch or expansion",
    "Expansion signal": "adding to the team",
}


def top_signal(company: dict):
    """The strongest piece of evidence, or None. Evidence is ordered jobs first, strongest tier first."""
    for evidence in company.get("signal_evidence") or []:
        if evidence.get("label") in SIGNAL_PHRASES:
            return evidence
    return None


def generate_personalization(company: dict, campaign=None) -> dict:
    campaign = validate_campaign(campaign) if campaign is not None else load_campaign()
    offer = campaign["offer"]
    result = {**company, "best_contact_name": None, "best_contact_email": None,
              "best_contact_title": None, "opener": None, "opener_evidence": None,
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
    prefix = f"{greeting}, " if greeting else ""
    signal = top_signal(company)
    if signal:
        opener = (f"{prefix}it looks like {company_name} is {SIGNAL_PHRASES[signal['label']]}. "
                  f"Is {offer['problem']} something you're looking to address?")
        reasoning = "Uses the enriched contact and the strongest account-specific signal (see opener_evidence)."
    else:
        opener = f"{prefix}is {offer['problem']} something {company_name} is looking to address?"
        reasoning = "Uses the enriched contact; no account-specific signal was found, so no timing claim is made."

    result.update(best_contact_name=name or None,
                  best_contact_email=contact["email"].strip(),
                  best_contact_title=contact.get("position"), opener=opener,
                  opener_evidence=signal, personalization_status="draft", reasoning=reasoning)
    return result


def main():
    with open(INPUT_PATH) as f:
        companies = json.load(f)
    campaign = load_campaign()
    results = [generate_personalization(company, campaign) for company in companies]
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Prepared {len(results)} accounts for review")


if __name__ == "__main__":
    main()
