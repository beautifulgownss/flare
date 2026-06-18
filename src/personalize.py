import json
import os
from dotenv import load_dotenv

load_dotenv()

MOCK_RESPONSES = {
    "stripe.com": {
        "best_contact_email": "kbognar@stripe.com",
        "best_contact_name": "Kevin Bognar",
        "best_contact_title": "Vice President of Sales",
        "opener": "Kevin, given Stripe's rapid expansion into agentic commerce, I'd love to show you how we're helping VP-level sales leaders automate their GTM enrichment stack.",
        "reasoning": "VP of Sales is the highest-value contact for a GTM tool — directly owns the pipeline and outbound motion."
    },
    "vercel.com": {
        "best_contact_email": "gaspar.garcia@vercel.com",
        "best_contact_name": "Gaspar Garcia",
        "best_contact_title": "Head of AI Research",
        "opener": "Gaspar, given Vercel's investment in AI infrastructure, I imagine your team is thinking hard about how AI fits into your own GTM motion — we're helping teams like yours automate exactly that.",
        "reasoning": "Head of AI Research is a better fit than Director of PMO — they'll immediately understand the technical value proposition of an AI-powered GTM tool."
    },
    "retool.com": {
        "best_contact_email": "david@retool.com",
        "best_contact_name": "David Hsu",
        "best_contact_title": "CEO",
        "opener": "David, Retool's positioning as the internal tools platform makes your team uniquely positioned to understand why we built our GTM enrichment pipeline the way we did — would love 15 minutes.",
        "reasoning": "CEO at a company this size is directly involved in GTM decisions and will immediately grasp the builder-first value prop."
    },
    "linear.app": {
        "best_contact_email": "casey@linear.app",
        "best_contact_name": "Casey Bertenthal",
        "best_contact_title": "Sales Director",
        "opener": "Casey, as Linear scales its sales motion beyond product-led growth, I'd love to show you how we're helping sales directors at dev-tool companies automate their account research and enrichment.",
        "reasoning": "Sales Director owns the outbound motion directly and will have immediate context on the pain points our tool solves."
    }
}

def generate_personalization(company: dict) -> dict:
    if company.get("recommendation") == "Low priority":
        return {
            "domain": company.get("domain"),
            "name": company.get("name"),
            "score": company.get("score"),
            "recommendation": "Low priority",
            "emails_found": company.get("emails_found"),
            "best_contact": None,
            "opener": None,
            "reasoning": "Skipped — low priority account"
        }

    domain = company.get("domain")
    mock = MOCK_RESPONSES.get(domain, {
        "best_contact_email": "unknown@" + domain,
        "best_contact_name": "Unknown",
        "best_contact_title": "Unknown",
        "opener": f"I noticed {company.get('name')} is doing interesting work — would love to connect.",
        "reasoning": "No mock response configured for this domain."
    })

    return {
        "domain": domain,
        "name": company.get("name"),
        "score": company.get("score"),
        "recommendation": company.get("recommendation"),
        "emails_found": company.get("emails_found"),
        **mock
    }


def main():
    with open("data/enriched/scored_companies.json", "r") as f:
        companies = json.load(f)

    results = []
    for company in companies:
        print(f"Personalizing {company.get('name')}...")
        result = generate_personalization(company)
        results.append(result)
        if result.get("opener"):
            print(f"  → {result.get('opener')}")
        else:
            print(f"  → Skipped")

    output_path = "data/enriched/personalized_companies.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Results written to {output_path}")

if __name__ == "__main__":
    main()