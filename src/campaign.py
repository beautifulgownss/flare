"""Validated, file-based campaign configuration shared by pipeline steps."""
import json
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "config" / "campaign.json"

# Used when campaign.json omits a "scoring" block. Scores are on a 0-10 scale.
DEFAULT_SCORING = {
    "weights": {"contactability": 0.5, "timing": 0.5},
    "tiers": {"high": 7.0, "medium": 5.0},
    "min_email_confidence": 70,
    "signal_lookback": "qdr:m3",
}


def _validate_scoring(scoring):
    if not isinstance(scoring, dict):
        raise ValueError("scoring must be an object")
    weights = scoring.get("weights")
    if not isinstance(weights, dict) or set(weights) != {"contactability", "timing"}:
        raise ValueError("scoring.weights must define exactly contactability and timing")
    if any(not isinstance(w, int | float) or w < 0 for w in weights.values()):
        raise ValueError("scoring.weights must be non-negative numbers")
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError("scoring.weights must sum to 1.0")
    tiers = scoring.get("tiers")
    if not isinstance(tiers, dict) or not all(isinstance(tiers.get(k), int | float) for k in ("high", "medium")):
        raise ValueError("scoring.tiers must define numeric high and medium thresholds")
    if not 0 <= tiers["medium"] < tiers["high"] <= 10:
        raise ValueError("scoring.tiers must satisfy 0 <= medium < high <= 10")
    confidence = scoring.get("min_email_confidence")
    if not isinstance(confidence, int | float) or not 0 <= confidence <= 100:
        raise ValueError("scoring.min_email_confidence must be between 0 and 100")
    if not isinstance(scoring.get("signal_lookback"), str) or not scoring["signal_lookback"].strip():
        raise ValueError("scoring.signal_lookback must be a nonempty string")


def validate_campaign(config):
    if not isinstance(config, dict):
        raise ValueError("Campaign must be an object")
    for field in ("buyer_roles", "excluded_roles"):
        values = config.get(field)
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"{field} must be a list of nonempty strings")
    if not config["buyer_roles"]:
        raise ValueError("At least one buyer role is required")
    offer = config.get("offer")
    if not isinstance(offer, dict):
        raise ValueError("offer must be an object")
    for field in ("name", "description", "problem", "cta", "sender_name"):
        if not isinstance(offer.get(field), str) or not offer[field].strip():
            raise ValueError(f"offer.{field} must be a nonempty string")
    scoring = {**DEFAULT_SCORING, **(config.get("scoring") or {})}
    _validate_scoring(scoring)
    config["scoring"] = scoring
    return config


def load_campaign(path=None):
    with open(path or os.environ.get("GTM_CAMPAIGN_CONFIG") or DEFAULT_PATH) as f:
        return validate_campaign(json.load(f))


def _contact_is_usable(contact, min_confidence):
    """Contacts need an email. Known-invalid or low-confidence emails are dropped.

    Hunter returns a 0-100 confidence and a verification status. Fixtures and
    older data may not have them; those contacts stay eligible but score lower.
    """
    if not (contact.get("email") or "").strip():
        return False
    if contact.get("verification_status") == "invalid":
        return False
    confidence = contact.get("confidence")
    return confidence is None or confidence >= min_confidence


def select_buyer(contacts, config):
    """Role order is priority; exclusions win. Only usable emails qualify.

    Returns (contact, role_priority) or (None, None).
    """
    min_confidence = config.get("scoring", DEFAULT_SCORING)["min_email_confidence"]
    ranked = []
    for index, contact in enumerate(contacts or []):
        title = str(contact.get("position") or "").casefold()
        if not _contact_is_usable(contact, min_confidence):
            continue
        if any(role.casefold() in title for role in config["excluded_roles"]):
            continue
        for priority, role in enumerate(config["buyer_roles"]):
            if role.casefold() in title:
                ranked.append((priority, index, contact))
                break
    if not ranked:
        return None, None
    priority, _, contact = min(ranked, key=lambda item: item[:2])
    return contact, priority
