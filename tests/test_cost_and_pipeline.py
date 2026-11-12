"""Real token cost, pitch-prompt proof handling, run history, and step order."""
from types import SimpleNamespace

import pytest

import pitch_pages
import run_pipeline
import tracker

OFFER = {"name": "Flare", "description": "Account research workflows.", "problem": "manual research",
         "cta": "Want a walkthrough?", "sender_name": "Courtney"}
COMPANY = {"name": "Acme", "domain": "acme.test",
           "signal_evidence": [{"label": "Funding signal", "title": "Acme raises Series B", "link": "https://acme.test/b"}]}


def test_prompt_without_proof_forbids_social_proof():
    prompt = pitch_pages.build_prompt(COMPANY, {}, OFFER, proof="")
    assert "<proof>\n" not in prompt
    assert '"proof_line"' not in prompt
    assert "Never invent" in prompt
    assert "Acme raises Series B" in prompt


def test_prompt_with_proof_includes_it():
    prompt = pitch_pages.build_prompt(COMPANY, {}, OFFER, proof="Cut research time 60% for a Series B SaaS team.")
    assert "<proof>\n" in prompt and "Cut research time 60%" in prompt
    assert '"proof_line"' in prompt


def valid_pitch(**extra):
    vp = {"title": "t", "body": "b", "signal_source": "s"}
    return {"headline": "h", "subheadline": "s", "value_props": [vp, vp, vp],
            "cta": {"text": "Book", "context": "c"}, "tone": "technical", **extra}


def test_unsupported_proof_line_is_dropped():
    data = valid_pitch(proof_line="Trusted by 500 companies")
    pitch_pages.validate_pitch_data(data, proof_required=False)
    assert "proof_line" not in data
    with pytest.raises(ValueError):
        pitch_pages.validate_pitch_data(valid_pitch(), proof_required=True)


def test_usage_cost_comes_from_response_tokens(monkeypatch):
    monkeypatch.setattr(pitch_pages, "INPUT_COST_PER_MTOK", 3.0)
    monkeypatch.setattr(pitch_pages, "OUTPUT_COST_PER_MTOK", 15.0)
    message = SimpleNamespace(usage=SimpleNamespace(input_tokens=2000, output_tokens=1000))
    assert pitch_pages.usage_of(message) == {"input_tokens": 2000, "output_tokens": 1000, "cost_usd": 0.021}


def test_run_log_records_real_cost_and_migrates_old_db(tmp_path, monkeypatch):
    db = tmp_path / "nested" / "runs.db"
    monkeypatch.setattr(tracker, "DB_PATH", str(db))
    tracker.init_db()
    tracker.init_db()  # idempotent: migrations only add missing columns
    companies = [{"domain": "acme.test", "name": "Acme", "composite_score": 7.0, "contactability_score": 8.0,
                  "total_signal_score": 6, "recommendation": "High priority", "final_recommendation": "High priority"}]
    tracker.log_run("run_1", companies, 1.5, llm_usage={"input_tokens": 2000, "output_tokens": 1000, "cost_usd": 0.021})
    tracker.log_run("run_2", companies, 1.5)  # no LLM step: cost is zero, not an estimate
    runs = {r["run_id"]: r for r in tracker.get_runs()}
    assert runs["run_1"]["estimated_token_cost"] == 0.021
    assert runs["run_1"]["llm_input_tokens"] == 2000
    assert runs["run_2"]["estimated_token_cost"] == 0


def test_signals_run_before_scoring_and_outreach():
    names = [name for name, _, _ in run_pipeline.STEPS]
    assert names.index("Signal Fetching") < names.index("Scoring") < names.index("Personalization")
    assert names.index("Personalization") < names.index("Sequence Generation")
    required = [required for _, _, required in run_pipeline.STEPS]
    assert required == sorted(required, reverse=True)  # optional integrations run last


def test_read_llm_usage_handles_missing_status(tmp_path):
    assert run_pipeline.read_llm_usage(tmp_path / "missing.json") == {}
    path = tmp_path / "status.json"
    path.write_text('{"usage": {"input_tokens": 5, "output_tokens": 1, "cost_usd": 0.1}}')
    assert run_pipeline.read_llm_usage(path)["cost_usd"] == 0.1
