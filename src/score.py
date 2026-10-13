import json
from campaign import load_campaign, select_buyer, validate_campaign

def mock_llm_score(company: dict, campaign=None) -> dict:
    """
    Mimics what an LLM would return when scoring a company.
    In Phase 2 we'll replace this with a real API call.
    """
    
    # Extract contact titles for scoring logic
    titles = [
        c.get("position", "") 
        for c in company.get("top_contacts", []) 
        if c.get("position")
    ]
    
    # Simple scoring rules based on title signals
    score = 5  # baseline
    reasons = []
    best_contact = None

    for contact in company.get("top_contacts", []):
        position = (contact.get("position") or "").lower()
        
        # High value titles
        if any(t in position for t in ["ceo", "founder", "president"]):
            score += 3
            reasons.append(f"Executive contact available: {contact.get('position')}")
            best_contact = contact
        elif any(t in position for t in ["vp", "vice president", "director"]):
            score += 2
            reasons.append(f"Senior contact available: {contact.get('position')}")
            if not best_contact:
                best_contact = contact
        elif any(t in position for t in ["head of", "manager", "lead"]):
            score += 1
            reasons.append(f"Mid-level contact available: {contact.get('position')}")
            if not best_contact:
                best_contact = contact

    if campaign is not None:
        validate_campaign(campaign)
        best_contact = select_buyer(company.get("top_contacts", []), campaign)
        # Contactability and buyer-role match, not firmographic ICP fit.
        score = 8 if best_contact else 3
        reasons = ([f"Target buyer available: {best_contact.get('position')}"]
                   if best_contact else ["No contact matches configured buyer roles with an email"])

    # emails found signal
    emails = company.get("emails_found", 0)
    if emails >= 10:
        score += 1
        reasons.append("High email coverage (10+)")
    elif emails == 0:
        score -= 2
        reasons.append("No emails found — low discoverability")

    # cap score at 10
    score = min(score, 10)

    return {
    "scoring_basis": "buyer_role_and_contactability" if campaign else "legacy_seniority",
    "domain": company.get("domain"),
    "name": company.get("name"),
    "score": min(score, 10),
    "emails_found": company.get("emails_found"),
    "reasons": reasons,
    "best_contact": best_contact,
    "recommendation": "High priority" if score >= 8 else "Medium priority" if score >= 6 else "Low priority"
}


def main():
    # Load enriched companies
    with open("data/enriched/companies.json", "r") as f:
        companies = json.load(f)

    campaign = load_campaign()
    results = []
    for company in companies:
        print(f"Scoring {company.get('name')}...")
        scored = mock_llm_score(company, campaign)
        results.append(scored)
        print(f"  Score: {scored['score']}/10 — {scored['recommendation']}")

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Save output
    output_path = "data/enriched/scored_companies.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Scored {len(results)} companies → {output_path}")
    print("\nPriority order:")
    for r in results:
        print(f"  {r['score']}/10 — {r['name']} ({r['recommendation']})")

if __name__ == "__main__":
    main()