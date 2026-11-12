import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from campaign import load_campaign, validate_campaign
from personalize import generate_personalization
from score import score_account
from sequence import generate_sequence


def test_target_role_beats_unrelated_executive():
    company = {"domain": "new.test", "emails_found": 5, "top_contacts": [
        {"position": "CEO", "email": "ceo@new.test"},
        {"position": "Revenue Operations Manager", "email": "ops@new.test"}]}
    result = score_account(company, None, load_campaign())
    assert result["best_contact"]["email"] == "ops@new.test"
    assert result["scoring_basis"] == "contactability_and_timing"


def test_exclusion_wins_and_missing_email_is_ineligible():
    config = load_campaign()
    company = {"emails_found": 10, "top_contacts": [
        {"position": "Sales Finance Director", "email": "finance@new.test"},
        {"position": "VP Sales", "email": None}]}
    result = score_account(company, None, config)
    assert result["best_contact"] is None
    assert result["recommendation"] == "Low priority"


def test_role_order_controls_selection():
    config = load_campaign()
    contacts = [{"position": "VP Sales", "email": "sales@new.test"},
                {"position": "RevOps Manager", "email": "ops@new.test"}]
    result = score_account({"emails_found": 5, "top_contacts": contacts}, None, config)
    assert result["best_contact"]["email"] == "ops@new.test"


def test_custom_offer_flows_into_all_drafts():
    config = load_campaign()
    config["offer"] = {"name": "Launch planning", "description": "I help teams plan product launches.",
                       "problem": "launch coordination", "cta": "Would a launch review help?",
                       "sender_name": "Alex"}
    company = {"name": "Acme", "recommendation": "High priority",
               "best_contact": {"first_name": "Sam", "email": "sam@acme.test"}}
    draft = generate_personalization(company, config)
    result = generate_sequence(draft)
    assert "launch coordination" in draft["opener"]
    assert config["offer"]["description"] in result["sequence"][0]["body"]
    assert config["offer"]["cta"] in result["sequence"][0]["body"]
    assert all(step["body"].endswith("Alex") for step in result["sequence"])
    assert "Launch planning" in result["sequence"][0]["subject"]
    assert "CRM" not in str(result["sequence"])


def test_invalid_config_fails_clearly():
    for bad in ({}, {"buyer_roles": [], "excluded_roles": [], "offer": {}},
                {"buyer_roles": "sales", "excluded_roles": [], "offer": {}}, None):
        try:
            validate_campaign(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid config accepted")


def test_scoring_config_is_validated():
    config = load_campaign()
    assert config["scoring"]["weights"]["contactability"] + config["scoring"]["weights"]["timing"] == 1
    for bad in ({"weights": {"contactability": 0.9, "timing": 0.9}}, {"tiers": {"high": 3, "medium": 5}},
                {"min_email_confidence": 150}):
        try:
            validate_campaign({**config, "scoring": bad})
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid scoring accepted: {bad}")


def test_opener_uses_signal_phrase_not_raw_title():
    config = load_campaign()
    company = {"name": "Acme", "recommendation": "High priority",
               "best_contact": {"first_name": "Sam", "email": "sam@acme.test"},
               "signal_evidence": [{"label": "Funding signal", "title": "Acme raises $40M Series B at 10x ARR",
                                    "link": "https://acme.test/blog/series-b"}]}
    draft = generate_personalization(company, config)
    assert "coming off recent funding news" in draft["opener"]
    assert "$40M" not in draft["opener"]
    assert draft["opener_evidence"]["link"] == "https://acme.test/blog/series-b"


def test_opener_without_signal_makes_no_timing_claim():
    company = {"name": "Acme", "recommendation": "Medium priority",
               "best_contact": {"first_name": "Sam", "email": "sam@acme.test"}}
    draft = generate_personalization(company, load_campaign())
    assert "it looks like" not in draft["opener"]
    assert draft["opener_evidence"] is None


def test_intro_email_greets_once():
    company = {"name": "Acme", "recommendation": "High priority",
               "best_contact": {"first_name": "Sam", "email": "sam@acme.test"},
               "signal_evidence": [{"label": "Funding signal", "title": "Acme raises Series B", "link": "x"}]}
    body = generate_sequence(generate_personalization(company, load_campaign()))["sequence"][0]["body"]
    assert body.startswith("Hi Sam,")
    assert body.count("Sam") == 1
