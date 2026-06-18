import json
import os

def mock_llm_score(company: dict) -> dict:
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

    results = []
    for company in companies:
        print(f"Scoring {company.get('name')}...")
        scored = mock_llm_score(company)
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