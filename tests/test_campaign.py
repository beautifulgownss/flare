import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from campaign import load_campaign, validate_campaign
from score import mock_llm_score
from personalize import generate_personalization
from sequence import generate_sequence


def test_target_role_beats_unrelated_executive():
    company = {"domain": "new.test", "emails_found": 5, "top_contacts": [
        {"position": "CEO", "email": "ceo@new.test"},
        {"position": "Revenue Operations Manager", "email": "ops@new.test"}]}
    result = mock_llm_score(company, load_campaign())
    assert result["best_contact"]["email"] == "ops@new.test"
    assert result["scoring_basis"] == "buyer_role_and_contactability"


def test_exclusion_wins_and_missing_email_is_ineligible():
    config = load_campaign()
    company = {"emails_found": 10, "top_contacts": [
        {"position": "Sales Finance Director", "email": "finance@new.test"},
        {"position": "VP Sales", "email": None}]}
    result = mock_llm_score(company, config)
    assert result["best_contact"] is None
    assert result["recommendation"] == "Low priority"


def test_role_order_controls_selection():
    config = load_campaign()
    contacts = [{"position": "VP Sales", "email": "sales@new.test"},
                {"position": "RevOps Manager", "email": "ops@new.test"}]
    result = mock_llm_score({"emails_found": 5, "top_contacts": contacts}, config)
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
