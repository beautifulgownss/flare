"""Score each account on contactability and timing, then assign a priority tier.

Contactability (0-10): does a configured buyer role have a usable email? Higher
priority roles and higher Hunter email confidence score higher. Company size
does not, so large companies with many listed emails no longer max out by default.

Timing (0-10): job and news signals tied to the account (see signals.py).

ICP fit is not modeled yet. It's the next scoring component, and the README says so.
"""
import json
from pathlib import Path

from campaign import load_campaign, select_buyer, validate_campaign

ENRICHED_PATH = "data/enriched/companies.json"
SIGNALS_PATH = "data/signals/signals.json"
OUTPUT_PATH = "data/scored_final/companies_final.json"

TOP_ROLE_SCORE = 10.0
ROLE_STEP = 1.5           # each lower-priority buyer role scores 1.5 less
MIN_ROLE_SCORE = 4.0
UNKNOWN_CONFIDENCE = 0.8  # multiplier when the provider gave no confidence
UNVERIFIED_STATUSES = {"accept_all", "unknown", "webmail", "disposable"}


def score_contactability(company: dict, campaign: dict) -> dict:
    """Return the 0-10 contactability score, the selected buyer, and reasons."""
    campaign = validate_campaign(campaign)
    contact, priority = select_buyer(company.get("top_contacts", []), campaign)
    if contact is None:
        return {"contactability_score": 0.0, "best_contact": None,
                "reasons": ["No contact matches a configured buyer role with a usable email"]}

    role_score = max(TOP_ROLE_SCORE - ROLE_STEP * priority, MIN_ROLE_SCORE)
    reasons = [f"Target buyer available: {contact.get('position')} (role priority {priority + 1})"]

    confidence = contact.get("confidence")
    if confidence is None:
        multiplier = UNKNOWN_CONFIDENCE
        reasons.append("Email confidence unknown")
    else:
        multiplier = 0.5 + confidence / 200  # 70 -> 0.85, 100 -> 1.0
        reasons.append(f"Email confidence {confidence}/100")

    status = contact.get("verification_status")
    if status in UNVERIFIED_STATUSES:
        multiplier *= 0.9
        reasons.append(f"Email not verified ({status})")
    elif status == "valid":
        reasons.append("Email verified")

    return {"contactability_score": round(role_score * multiplier, 1),
            "best_contact": contact, "reasons": reasons}


def tier_for(score: float, tiers: dict) -> str:
    if score >= tiers["high"]:
        return "High priority"
    if score >= tiers["medium"]:
        return "Medium priority"
    return "Low priority"


def compute_composite_score(contactability: float, timing: float, scoring: dict) -> dict:
    weights = scoring["weights"]
    composite = round(contactability * weights["contactability"] + timing * weights["timing"], 1)
    composite = min(composite, 10.0)
    return {"composite_score": composite, "recommendation": tier_for(composite, scoring["tiers"])}


def score_account(company: dict, signals: dict | None, campaign: dict) -> dict:
    """Combine contactability and timing into the record every later step reads."""
    contact = score_contactability(company, campaign)
    signals = signals or {}
    timing = float(signals.get("total_signal_score", 0))
    composite = compute_composite_score(contact["contactability_score"], timing, campaign["scoring"])
    reasons = contact["reasons"] + signals.get("job_reasons", []) + signals.get("news_reasons", [])
    if not signals.get("signal_evidence"):
        reasons.append("No account-specific hiring or news signals found")
    return {
        **company,
        "scoring_basis": "contactability_and_timing",
        "score": contact["contactability_score"],  # kept for dashboard compatibility
        "contactability_score": contact["contactability_score"],
        "best_contact": contact["best_contact"],
        "job_score": signals.get("job_score", 0),
        "job_reasons": signals.get("job_reasons", []),
        "news_score": signals.get("news_score", 0),
        "news_reasons": signals.get("news_reasons", []),
        "total_signal_score": timing,
        "signal_evidence": signals.get("signal_evidence", []),
        "composite_score": composite["composite_score"],
        "recommendation": composite["recommendation"],
        "final_recommendation": composite["recommendation"],
        "reasons": reasons,
    }


def tier_distribution(accounts: list) -> dict:
    counts = {"High priority": 0, "Medium priority": 0, "Low priority": 0}
    for account in accounts:
        counts[account["final_recommendation"]] += 1
    return counts


def main():
    campaign = load_campaign()
    with open(ENRICHED_PATH) as f:
        companies = [c for c in json.load(f) if not c.get("error")]
    try:
        with open(SIGNALS_PATH) as f:
            signals_by_domain = {s["domain"]: s for s in json.load(f)}
    except FileNotFoundError:
        print(f"  WARNING: {SIGNALS_PATH} missing; timing scores will be 0")
        signals_by_domain = {}

    results = [score_account(c, signals_by_domain.get(c.get("domain")), campaign) for c in companies]
    results.sort(key=lambda r: r["composite_score"], reverse=True)

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nScored {len(results)} accounts -> {OUTPUT_PATH}")
    for r in results:
        print(f"  {r['composite_score']}/10  {r['name']}  (contactability {r['contactability_score']}, "
              f"timing {r['total_signal_score']})  {r['final_recommendation']}")
    dist = tier_distribution(results)
    print(f"  Tiers: {dist}")
    if results and dist["High priority"] / len(results) > 0.5:
        print("  WARNING: over half the accounts are High priority; tiers may be too loose for this list")


if __name__ == "__main__":
    main()
