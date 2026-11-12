import html
import json
import os
import re
import sys
import time
from datetime import UTC, datetime

import anthropic
from dotenv import load_dotenv

from campaign import load_campaign

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
MAX_TOKENS = 2048
# USD per million tokens. Set these to your model's current list price; the
# run log reports cost from actual token usage multiplied by these rates.
INPUT_COST_PER_MTOK = float(os.getenv("ANTHROPIC_INPUT_COST_PER_MTOK", "3"))
OUTPUT_COST_PER_MTOK = float(os.getenv("ANTHROPIC_OUTPUT_COST_PER_MTOK", "15"))

COMPANIES_PATH = "data/scored_final/companies_final.json"
PERSONALIZED_PATH = "data/enriched/personalized_companies.json"
STATUS_PATH = "data/pitch_pages_status.json"
PAGES_DIR = "pages"
PROOF_PATH = "context/proof.md"

ALLOWED_TONES = {"technical", "executive", "operational"}

PROMPT_TEMPLATE = """You are writing a short, personalized pitch page for one B2B account.

{product_block}

<prospect>
Company: {company_name}
Industry: {industry}
Composite score: {composite_score}
Best contact: {contact_name}, {contact_role}
Account-specific signals (each line is evidence you may cite):
{serper_signals}
Prior personalization context:
{existing_opener_context}
</prospect>

Rules:
- Only state facts that appear in <offer>, <proof>, or <prospect>. Never invent customers, results, metrics, quotes, or logos.
- Every value_prop MUST cite one line from the account-specific signals in signal_source. If there are no signals, cite "industry" and keep the claim general and factual.
- Exactly 3 value_props.
- Headline names their likely problem, not the offer's features.
- Match tone to persona: technical for engineering roles, executive for C-suite/VP, operational for managers.
- {proof_rule}
- No buzzwords: "leverage", "unlock", "seamless", "empower" are banned.
- Respond ONLY with valid JSON matching the provided schema. No markdown fences, no preamble.

JSON schema:
{{
  "company_slug": "acme-logistics",
  "headline": "string, positions the offer against THEIR named problem, max 12 words",
  "subheadline": "string, one sentence expanding the headline, max 25 words",
  "value_props": [
    {{
      "title": "string, 3-6 words",
      "body": "string, 1-2 sentences tying the benefit to a cited signal or their industry",
      "signal_source": "string, the signal line or 'industry'"
    }}
  ],
{proof_schema}  "cta": {{
    "text": "string, action verb, max 5 words",
    "context": "string, one sentence on why now, grounded in a cited signal if one exists"
  }},
  "tone": "string, one of: technical, executive, operational (picked based on contact persona)"
}}
"""


def load_proof(path: str = PROOF_PATH) -> str:
    """Real, verifiable proof points (results, clients with permission). Empty if none exist yet."""
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def build_product_block(offer: dict, proof: str) -> str:
    block = (f"<offer>\nName: {offer['name']}\nWhat it is: {offer['description']}\n"
             f"Problem it addresses: {offer['problem']}\nFrom: {offer['sender_name']}, Flare\n</offer>")
    if proof:
        block += f"\n<proof>\n{proof}\n</proof>"
    return block


def load_companies() -> list:
    with open(COMPANIES_PATH) as f:
        return json.load(f)


def load_personalized_map() -> dict:
    try:
        with open(PERSONALIZED_PATH) as f:
            entries = json.load(f)
    except FileNotFoundError:
        return {}
    return {normalize_domain(e.get("domain")): e for e in entries if e.get("domain")}


def normalize_domain(domain: str) -> str:
    return (domain or "").strip().lower()


def filter_high_priority(companies: list) -> list:
    return [c for c in companies if c.get("final_recommendation") == "High priority"]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return slug or "unnamed-company"


def resolve_contact(company: dict, personalized: dict) -> tuple:
    if personalized:
        name = (personalized.get("best_contact_name") or "").strip()
        role = (personalized.get("best_contact_title") or "").strip()
        if name:
            return name, (role or "Unknown")

    best_contact = company.get("best_contact") or {}
    full_name = f"{best_contact.get('first_name') or ''} {best_contact.get('last_name') or ''}".strip()
    if full_name:
        return full_name, (best_contact.get("position") or "Unknown")

    return "Unknown", "Unknown"


def build_signal_lines(company: dict) -> str:
    lines = [f"- {e.get('label')}: {e.get('title')} ({e.get('link')})" for e in company.get("signal_evidence", [])]
    if not lines:
        return "No account-specific signals found. Use industry context only."
    return "\n".join(lines)


def resolve_opener_context(personalized: dict) -> str:
    if not personalized:
        return "No prior personalization context available."
    parts = [p for p in [personalized.get("opener"), personalized.get("reasoning")] if p]
    return "\n".join(parts) if parts else "No prior personalization context available."


def build_prompt(company: dict, personalized: dict, offer: dict, proof: str = "") -> str:
    contact_name, contact_role = resolve_contact(company, personalized)
    if proof:
        proof_rule = "proof_line must restate one item from <proof> exactly; do not embellish it."
        proof_schema = '  "proof_line": "string, one sentence taken from <proof>",\n'
    else:
        proof_rule = "There is no <proof> block, so do not include a proof_line or any social proof."
        proof_schema = ""
    return PROMPT_TEMPLATE.format(
        product_block=build_product_block(offer, proof),
        proof_rule=proof_rule,
        proof_schema=proof_schema,
        company_name=company.get("name", "Unknown"),
        industry=company.get("industry") or "Unknown",
        composite_score=company.get("composite_score", "Unknown"),
        contact_name=contact_name,
        contact_role=contact_role,
        serper_signals=build_signal_lines(company),
        existing_opener_context=resolve_opener_context(personalized),
    )


def call_llm(client: "anthropic.Anthropic", prompt: str):
    return client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )


def extract_json_text(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def validate_pitch_data(data: dict, proof_required: bool = False) -> None:
    required_keys = ["headline", "subheadline", "value_props", "cta", "tone"]
    if proof_required:
        required_keys.append("proof_line")
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key in LLM response: {key}")
    if not proof_required:
        data.pop("proof_line", None)  # never render unsupported social proof

    value_props = data["value_props"]
    if not isinstance(value_props, list) or len(value_props) != 3:
        raise ValueError("value_props must contain exactly 3 items")
    for vp in value_props:
        for field in ("title", "body", "signal_source"):
            if not vp.get(field):
                raise ValueError(f"value_prop missing required field: {field}")

    cta = data["cta"]
    if not cta.get("text") or not cta.get("context"):
        raise ValueError("cta must include both text and context")

    if data["tone"] not in ALLOWED_TONES:
        raise ValueError(f"tone must be one of {ALLOWED_TONES}, got {data['tone']!r}")


def parse_and_validate_response(message, proof_required: bool = False) -> dict:
    if message.stop_reason not in ("end_turn", "stop_sequence"):
        raise ValueError(f"Unexpected stop_reason: {message.stop_reason}")

    raw_text = message.content[0].text
    data = json.loads(extract_json_text(raw_text))
    validate_pitch_data(data, proof_required)
    return data


def usage_of(message) -> dict:
    """Actual token usage from the API response, priced at the configured rates."""
    usage = getattr(message, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    cost = input_tokens / 1e6 * INPUT_COST_PER_MTOK + output_tokens / 1e6 * OUTPUT_COST_PER_MTOK
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "cost_usd": round(cost, 6)}


def render_html(company: dict, pitch_data: dict) -> str:
    headline = html.escape(pitch_data["headline"])
    subheadline = html.escape(pitch_data["subheadline"])
    proof_html = (f'<p class="proof">{html.escape(pitch_data["proof_line"])}</p>'
                  if pitch_data.get("proof_line") else "")
    cta_text = html.escape(pitch_data["cta"]["text"])
    cta_context = html.escape(pitch_data["cta"]["context"])
    tone = html.escape(pitch_data["tone"])
    company_name = html.escape(company.get("name", ""))

    value_prop_cards = "\n".join(
        f"""
        <div class="value-prop">
          <h3>{html.escape(vp["title"])}</h3>
          <p>{html.escape(vp["body"])}</p>
          <span class="signal">{html.escape(vp["signal_source"])}</span>
        </div>"""
        for vp in pitch_data["value_props"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} | Flare</title>
<style>
  :root {{
    --ink: #1a1a1a;
    --coral: #ff6b4a;
    --pool: #3d7ea6;
    --canvas: #faf7f2;
    --muted: #6b6b6b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--canvas);
    color: var(--ink);
    line-height: 1.5;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 64px 24px; }}
  .kicker {{
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 12px;
    font-weight: 700;
    color: var(--coral);
    margin: 0 0 12px;
  }}
  h1 {{ font-size: 40px; line-height: 1.15; margin: 0 0 16px; }}
  .sub {{ font-size: 18px; color: var(--muted); margin: 0 0 40px; }}
  .value-props {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
  }}
  .value-prop {{
    border: 2px solid var(--ink);
    padding: 20px;
    background: white;
  }}
  .value-prop h3 {{ margin: 0 0 8px; font-size: 16px; }}
  .value-prop p {{ margin: 0 0 12px; font-size: 14px; color: var(--ink); }}
  .value-prop .signal {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 11px;
    color: var(--pool);
  }}
  .proof {{
    border-left: 4px solid var(--coral);
    padding: 12px 20px;
    font-style: italic;
    color: var(--muted);
    margin: 0 0 40px;
  }}
  .cta {{
    background: var(--ink);
    color: white;
    padding: 32px;
    text-align: center;
  }}
  .cta .btn {{
    display: inline-block;
    background: var(--coral);
    color: white;
    font-weight: 700;
    padding: 14px 28px;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 14px;
  }}
  .cta p {{ margin: 0; font-size: 14px; opacity: 0.85; }}
  .footer {{
    margin-top: 32px;
    font-size: 12px;
    color: var(--muted);
    text-align: center;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <p class="kicker">For {company_name} · {tone} briefing</p>
    <h1>{headline}</h1>
    <p class="sub">{subheadline}</p>

    <div class="value-props">
      {value_prop_cards}
    </div>

    {proof_html}

    <div class="cta">
      <div class="btn">{cta_text}</div>
      <p>{cta_context}</p>
    </div>

    <p class="footer">Prepared by Flare from public information about {company_name}. flaregtm.com</p>
  </div>
</body>
</html>
"""


def write_page(slug: str, html_str: str) -> str:
    os.makedirs(PAGES_DIR, exist_ok=True)
    page_path = os.path.join(PAGES_DIR, f"{slug}.html")
    with open(page_path, "w") as f:
        f.write(html_str)
    return page_path


def generate_pitch_page_for_company(client: "anthropic.Anthropic", company: dict, personalized_map: dict,
                                    offer: dict, proof: str = "") -> dict:
    name = company.get("name")
    domain = company.get("domain")
    slug = slugify(name)
    start = time.time()
    usage = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}

    try:
        personalized = personalized_map.get(normalize_domain(domain))
        prompt = build_prompt(company, personalized, offer, proof)
        message = call_llm(client, prompt)
        usage = usage_of(message)
        pitch_data = parse_and_validate_response(message, proof_required=bool(proof))
        page_path = write_page(slug, render_html(company, pitch_data))

        duration_ms = round((time.time() - start) * 1000, 1)
        print(f"✅ Generated pitch page: {name} ({domain}) → {page_path}")
        return {
            "name": name,
            "domain": domain,
            "company_slug": slug,
            "status": "success",
            "action": "generated",
            "page_path": page_path,
            "duration_ms": duration_ms,
            "usage": usage,
            "error": None,
        }
    except Exception as e:
        duration_ms = round((time.time() - start) * 1000, 1)
        print(f"❌ Failed pitch page for {name} ({domain}): {e}")
        return {
            "name": name,
            "domain": domain,
            "company_slug": slug,
            "status": "failed",
            "action": "generated",
            "page_path": None,
            "duration_ms": duration_ms,
            "usage": usage,
            "error": str(e),
        }


def generate_all() -> dict:
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is not set — skipping pitch page generation.")
        status_report = {
            "last_generated": datetime.now(UTC).isoformat(),
            "total": 0,
            "succeeded": 0,
            "failed": 0,
            "accounts": [],
            "error": "ANTHROPIC_API_KEY is not set",
        }
        with open(STATUS_PATH, "w") as f:
            json.dump(status_report, f, indent=2)
        sys.exit(1)

    companies = filter_high_priority(load_companies())
    personalized_map = load_personalized_map()
    offer = load_campaign()["offer"]
    proof = load_proof()
    print(f"Generating pitch pages for {len(companies)} high-priority accounts...")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = [generate_pitch_page_for_company(client, c, personalized_map, offer, proof) for c in companies]

    status_report = {
        "last_generated": datetime.now(UTC).isoformat(),
        "total": len(results),
        "succeeded": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "model": MODEL,
        "usage": {
            "input_tokens": sum(r["usage"]["input_tokens"] for r in results),
            "output_tokens": sum(r["usage"]["output_tokens"] for r in results),
            "cost_usd": round(sum(r["usage"]["cost_usd"] for r in results), 6),
        },
        "accounts": results,
    }

    with open(STATUS_PATH, "w") as f:
        json.dump(status_report, f, indent=2)

    print(f"\nPitch page status written to {STATUS_PATH}")
    return status_report


if __name__ == "__main__":
    generate_all()
