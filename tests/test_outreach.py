import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from personalize import generate_personalization
from sequence import generate_sequence


def account(domain="new-company.test", **overrides):
    return {"domain": domain, "name": "New Company", "score": 8,
            "recommendation": "High priority",
            "best_contact": {"first_name": "Jamie", "last_name": "Lee",
                             "email": "jamie@new-company.test", "position": "VP Sales"},
            **overrides}


def test_unseen_company_gets_contact_backed_three_step_draft():
    draft = generate_personalization(account())
    sequence = generate_sequence(draft)
    assert draft["best_contact_email"] == "jamie@new-company.test"
    assert draft["best_contact_name"] == "Jamie Lee"
    assert len(sequence["sequence"]) == 3
    assert [s["type"] for s in sequence["sequence"]] == ["intro", "follow_up", "breakup"]
    assert sequence["requires_review"] is True
    assert sequence["generation_mode"] == "template"


def test_previous_sample_domain_does_not_override_enriched_contact():
    draft = generate_personalization(account(domain="stripe.com"))
    assert draft["best_contact_email"] == "jamie@new-company.test"
    assert "Kevin" not in draft["opener"]


def test_missing_contact_never_invents_email_or_sequence():
    for contact in (None, {}, {"email": ""}, {"email": "   "}):
        draft = generate_personalization(account(best_contact=contact))
        assert draft["best_contact_email"] is None
        assert draft["opener"] is None
        assert generate_sequence(draft)["sequence"] is None


def test_low_priority_skips_even_with_contact():
    draft = generate_personalization(account(recommendation="Low priority"))
    result = generate_sequence(draft)
    assert result["sequence"] is None
    assert result["reason"] == "Low priority account"


def test_sequence_rejects_contact_email_mismatch():
    draft = generate_personalization(account())
    draft["best_contact_email"] = "invented@example.test"
    assert generate_sequence(draft)["sequence"] is None


def test_unknown_name_uses_domain_without_none_in_copy():
    draft = generate_personalization(account(name=None, best_contact={"email": "person@example.test"}))
    result = generate_sequence(draft)
    assert "new-company.test" in draft["opener"]
    assert "None" not in str(result["sequence"])
