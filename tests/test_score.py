"""Contactability, composite scoring, and tier spread."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from campaign import load_campaign
from score import compute_composite_score, score_account, score_contactability, tier_distribution

CAMPAIGN = load_campaign()


def contact(position, email="a@acme.test", confidence=None, status=None):
    return {"first_name": "A", "position": position, "email": email,
            "confidence": confidence, "verification_status": status}


def test_no_buyer_scores_zero():
    result = score_contactability({"emails_found": 50, "top_contacts": [contact("CEO")]}, CAMPAIGN)
    assert result["contactability_score"] == 0.0
    assert result["best_contact"] is None


def test_email_count_no_longer_inflates_score():
    few = score_contactability({"emails_found": 1, "top_contacts": [contact("RevOps Manager", confidence=90)]}, CAMPAIGN)
    many = score_contactability({"emails_found": 500, "top_contacts": [contact("RevOps Manager", confidence=90)]}, CAMPAIGN)
    assert few["contactability_score"] == many["contactability_score"]


def test_role_priority_and_confidence_change_the_score():
    top = score_contactability({"top_contacts": [contact("Revenue Operations Lead", confidence=100, status="valid")]}, CAMPAIGN)
    lower = score_contactability({"top_contacts": [contact("Marketing Operations Manager", confidence=100)]}, CAMPAIGN)
    unknown = score_contactability({"top_contacts": [contact("Revenue Operations Lead")]}, CAMPAIGN)
    assert top["contactability_score"] == 10.0
    assert lower["contactability_score"] < top["contactability_score"]
    assert unknown["contactability_score"] == 8.0


def test_low_confidence_and_invalid_emails_are_dropped():
    company = {"top_contacts": [contact("VP Sales", confidence=40), contact("RevOps", status="invalid")]}
    assert score_contactability(company, CAMPAIGN)["best_contact"] is None


def test_unverified_email_is_discounted():
    valid = score_contactability({"top_contacts": [contact("RevOps", confidence=90, status="valid")]}, CAMPAIGN)
    risky = score_contactability({"top_contacts": [contact("RevOps", confidence=90, status="accept_all")]}, CAMPAIGN)
    assert risky["contactability_score"] < valid["contactability_score"]


def test_contactability_alone_cannot_reach_high_priority():
    result = score_account({"domain": "acme.test", "top_contacts": [contact("Revenue Operations Manager", confidence=100)]}, None, CAMPAIGN)
    assert result["composite_score"] == 5.0
    assert result["recommendation"] == "Medium priority"
    assert "No account-specific hiring or news signals found" in result["reasons"]


def test_score_account_carries_signal_evidence():
    signals = {"total_signal_score": 6, "job_score": 3, "job_reasons": ["Hiring senior sales leader: VP Sales"],
               "signal_evidence": [{"label": "Hiring senior sales leader", "title": "VP Sales", "link": "https://acme.test/jobs/1"}]}
    result = score_account({"domain": "acme.test", "top_contacts": [contact("Revenue Operations Manager", confidence=100)]}, signals, CAMPAIGN)
    assert result["composite_score"] == 8.0
    assert result["recommendation"] == "High priority"
    assert result["final_recommendation"] == "High priority"
    assert result["signal_evidence"][0]["link"] == "https://acme.test/jobs/1"


def test_composite_uses_campaign_weights_and_tiers():
    scoring = {**CAMPAIGN["scoring"], "weights": {"contactability": 0.2, "timing": 0.8}}
    out = compute_composite_score(10, 5, scoring)
    assert out["composite_score"] == 6.0
    assert out["recommendation"] == "Medium priority"


def test_tier_distribution_counts():
    accounts = [{"final_recommendation": "High priority"}, {"final_recommendation": "Low priority"}, {"final_recommendation": "Low priority"}]
    assert tier_distribution(accounts)["Low priority"] == 2
