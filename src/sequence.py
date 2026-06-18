import json
import os
from dotenv import load_dotenv

load_dotenv()

MOCK_SEQUENCES = {
    "stripe.com": {
        "contact": "Kevin Bognar",
        "title": "Vice President of Sales",
        "email": "kbognar@stripe.com",
        "sequence": [
            {
                "step": 1,
                "type": "intro",
                "subject": "GTM enrichment → Stripe's agentic commerce push",
                "body": """Hi Kevin,

Noticed Stripe has been expanding hard into agentic commerce — the Head of Agentic Commerce hire was a signal hard to miss.

We built a pipeline that automatically enriches accounts, scores them for ICP fit, and generates personalized openers using AI. Sales teams using it are cutting account research time from 45 minutes to under 2.

Worth a 15-minute look?

Courtney"""
            },
            {
                "step": 2,
                "type": "follow_up",
                "subject": "Re: GTM enrichment → Stripe's agentic commerce push",
                "body": """Hi Kevin,

Following up on my note from last week.

One thing that might be relevant for Stripe specifically: our pipeline handles high-volume account lists without losing personalization quality — which I imagine matters as you scale the agentic commerce motion.

Happy to show you a live demo on your own target accounts.

Courtney"""
            },
            {
                "step": 3,
                "type": "breakup",
                "subject": "Closing the loop",
                "body": """Hi Kevin,

I'll stop following up after this — I know you're busy.

If automating account research ever becomes a priority, I'm at courtney@example.com.

Either way, good luck with the agentic commerce build — it's genuinely exciting work.

Courtney"""
            }
        ]
    },
    "vercel.com": {
        "contact": "Gaspar Garcia",
        "title": "Head of AI Research",
        "email": "gaspar.garcia@vercel.com",
        "sequence": [
            {
                "step": 1,
                "type": "intro",
                "subject": "AI in your GTM motion — not just your product",
                "body": """Hi Gaspar,

You're thinking about AI in Vercel's product every day — curious if anyone is thinking about AI in Vercel's GTM motion.

We built a pipeline that uses LLMs to score accounts, select the right contact, and generate personalized outreach at scale. The same principles you'd apply to a good AI product — structured outputs, eval-first design, measurable quality.

Would love to show you what that looks like in practice.

Courtney"""
            },
            {
                "step": 2,
                "type": "follow_up",
                "subject": "Re: AI in your GTM motion — not just your product",
                "body": """Hi Gaspar,

Quick follow-up — I thought this might resonate given your background.

The part that tends to surprise technical folks: the hardest problem isn't the LLM call, it's the data quality upstream. Bad enrichment data produces bad personalization no matter how good your prompt is.

Happy to walk through how we handle that if it's useful.

Courtney"""
            },
            {
                "step": 3,
                "type": "breakup",
                "subject": "Closing the loop",
                "body": """Hi Gaspar,

Last note from me — if AI-powered GTM tooling ever becomes relevant, I'm easy to find.

Appreciate the work you're doing on Vercel's AI infrastructure. Following it closely.

Courtney"""
            }
        ]
    },
    "retool.com": {
        "contact": "David Hsu",
        "title": "CEO",
        "email": "david@retool.com",
        "sequence": [
            {
                "step": 1,
                "type": "intro",
                "subject": "Built this with the same philosophy as Retool",
                "body": """Hi David,

Retool's thesis is that internal tools shouldn't require a full eng sprint to build. We applied the same thinking to GTM infrastructure.

We built a pipeline that enriches accounts, scores them for ICP fit, and generates personalized outreach — all in a system a GTM engineer can own and extend without touching a CRM vendor's UI.

Given what you've built at Retool, I think you'd have opinions on this. Worth 15 minutes?

Courtney"""
            },
            {
                "step": 2,
                "type": "follow_up",
                "subject": "Re: Built this with the same philosophy as Retool",
                "body": """Hi David,

Following up — one thing I didn't mention: the whole pipeline outputs to a React dashboard that a sales team can actually use.

It felt wrong to build a GTM engineering tool that only lives in a terminal. You'd probably agree.

Courtney"""
            },
            {
                "step": 3,
                "type": "breakup",
                "subject": "Closing the loop",
                "body": """Hi David,

Last one from me.

If you ever want to see what a builder-first GTM stack looks like in practice, I'm at courtney@example.com.

Good luck with Retool — it's genuinely one of the most interesting companies in the space.

Courtney"""
            }
        ]
    },
    "linear.app": {
        "contact": "Casey Bertenthal",
        "title": "Sales Director",
        "email": "casey@linear.app",
        "sequence": [
            {
                "step": 1,
                "type": "intro",
                "subject": "Scaling Linear's outbound beyond PLG",
                "body": """Hi Casey,

Product-led growth gets you to a point — then someone has to build the outbound motion. Looks like that's you.

We built a pipeline that automates the research-heavy part of outbound: enriching accounts, scoring them for fit, and generating personalized first lines using AI. Sales directors at dev-tool companies are using it to run leaner, faster prospecting.

Worth a look?

Courtney"""
            },
            {
                "step": 2,
                "type": "follow_up",
                "subject": "Re: Scaling Linear's outbound beyond PLG",
                "body": """Hi Casey,

Following up quickly — the part most relevant to a PLG-to-outbound transition: our scoring logic prioritizes accounts already showing product signals, so your reps are calling people who've already expressed intent.

Happy to show you how that works on Linear's actual target accounts.

Courtney"""
            },
            {
                "step": 3,
                "type": "breakup",
                "subject": "Closing the loop",
                "body": """Hi Casey,

I'll leave it here.

If automating account research becomes a priority as you scale Linear's outbound, I'm easy to find.

Good luck with the motion — PLG companies building outbound is one of the more interesting GTM challenges right now.

Courtney"""
            }
        ]
    }
}


def generate_sequence(company: dict) -> dict:
    """
    Mock version of LLM sequence generation.
    Replace with real OpenAI/Anthropic call when API keys are ready.
    """

    if company.get("recommendation") == "Low priority":
        return {
            "domain": company.get("domain"),
            "name": company.get("name"),
            "score": company.get("score"),
            "recommendation": "Low priority",
            "sequence": None,
            "reason": "Skipped — low priority account"
        }

    domain = company.get("domain")
    mock = MOCK_SEQUENCES.get(domain, {
        "contact": company.get("best_contact_name", "there"),
        "title": company.get("best_contact_title", ""),
        "email": company.get("best_contact_email", ""),
        "sequence": [
            {
                "step": 1,
                "type": "intro",
                "subject": f"Quick question for {company.get('name')}",
                "body": f"Hi,\n\nWe built a GTM enrichment pipeline that might be relevant for {company.get('name')}.\n\nWorth a quick look?\n\nCourtney"
            }
        ]
    })

    return {
        "domain": domain,
        "name": company.get("name"),
        "score": company.get("score"),
        "recommendation": company.get("recommendation"),
        "contact": mock.get("contact"),
        "title": mock.get("title"),
        "email": mock.get("email"),
        "sequence": mock.get("sequence")
    }


def main():
    with open("data/enriched/personalized_companies.json", "r") as f:
        companies = json.load(f)

    results = []
    for company in companies:
        print(f"Generating sequence for {company.get('name')}...")
        result = generate_sequence(company)
        results.append(result)
        if result.get("sequence"):
            print(f"  → {len(result['sequence'])} emails generated")
        else:
            print(f"  → Skipped")

    output_path = "data/sequences/sequences.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Sequences written to {output_path}")


if __name__ == "__main__":
    main()