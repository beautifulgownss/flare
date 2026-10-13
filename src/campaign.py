"""Validated, file-based campaign configuration shared by pipeline steps."""
import json
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "config" / "campaign.json"


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
    return config


def load_campaign(path=None):
    with open(path or os.environ.get("GTM_CAMPAIGN_CONFIG") or DEFAULT_PATH) as f:
        return validate_campaign(json.load(f))


def select_buyer(contacts, config):
    """Role order is priority; exclusions win. Only supplied emails qualify."""
    ranked = []
    for index, contact in enumerate(contacts or []):
        title = str(contact.get("position") or "").casefold()
        if not (contact.get("email") or "").strip():
            continue
        if any(role.casefold() in title for role in config["excluded_roles"]):
            continue
        for priority, role in enumerate(config["buyer_roles"]):
            if role.casefold() in title:
                ranked.append((priority, index, contact))
                break
    return min(ranked, key=lambda item: item[:2])[2] if ranked else None
