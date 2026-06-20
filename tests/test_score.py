import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from score import mock_llm_score


def test_ceo_contact_scores_high():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 5,
        "top_contacts": [
            {"first_name": "Jane", "last_name": "Doe", "position": "CEO"}
        ]
    }
    result = mock_llm_score(company)
    assert result["score"] == 8
    assert result["best_contact"]["position"] == "CEO"
    assert "Executive contact available: CEO" in result["reasons"]


def test_no_contacts_keeps_baseline():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 5,
        "top_contacts": []
    }
    result = mock_llm_score(company)
    assert result["score"] == 5
    assert result["best_contact"] is None


def test_high_email_coverage_adds_point():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 10,
        "top_contacts": []
    }
    result = mock_llm_score(company)
    assert result["score"] == 6
    assert "High email coverage (10+)" in result["reasons"]


def test_zero_emails_penalizes_score():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 0,
        "top_contacts": []
    }
    result = mock_llm_score(company)
    assert result["score"] == 3
    assert "discoverability" in result["reasons"][0]


def test_score_caps_at_ten():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 10,
        "top_contacts": [
            {"first_name": "A", "last_name": "B", "position": "CEO"},
            {"first_name": "C", "last_name": "D", "position": "VP of Sales"},
            {"first_name": "E", "last_name": "F", "position": "Head of Marketing"}
        ]
    }
    result = mock_llm_score(company)
    assert result["score"] == 10


def test_best_contact_prefers_highest_tier():
    company = {
        "domain": "example.com",
        "name": "Example Co",
        "emails_found": 5,
        "top_contacts": [
            {"first_name": "A", "last_name": "B", "position": "Manager"},
            {"first_name": "C", "last_name": "D", "position": "CEO"}
        ]
    }
    result = mock_llm_score(company)
    assert result["best_contact"]["position"] == "CEO"


def test_recommendation_thresholds():
    high = mock_llm_score({
        "domain": "a.com",
        "name": "A",
        "emails_found": 10,
        "top_contacts": [{"position": "CEO"}]
    })
    assert high["recommendation"] == "High priority"

    low = mock_llm_score({
        "domain": "b.com",
        "name": "B",
        "emails_found": 0,
        "top_contacts": []
    })
    assert low["recommendation"] == "Low priority"