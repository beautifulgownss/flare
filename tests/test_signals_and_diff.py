"""Pure-logic tests for live-signal scoring, composite weighting, and score diffs."""
from unittest.mock import patch

import pytest

import diff
from signals import compute_composite_score, score_job_results, score_news_results


def result(title, snippet=""):
    return {"title": title, "snippet": snippet}


class TestSignalScoring:
    def test_job_tiers(self):
        score, reasons = score_job_results([
            result("Acme is hiring a VP of Sales"),
            result("Account Executive, Mid-Market"),
            result("Demand Gen Lead"),
        ])
        assert score == 5  # 3 + 2 + 1 = 6, capped at 5
        assert reasons[0].startswith("Hiring senior sales leader")
        assert reasons[1].startswith("Scaling sales team")
        assert reasons[2].startswith("Growing GTM team")

    def test_one_tier_per_result(self):
        score, reasons = score_job_results([result("VP of Sales and Account Executive roles")])
        assert score == 3
        assert len(reasons) == 1

    def test_acronyms_do_not_match_inside_words(self):
        score, _ = score_job_results([result("Engineers across microservices teams")])
        assert score == 0
        score, _ = score_job_results([result("Acme names new CRO")])
        assert score == 3

    def test_news_does_not_match_new(self):
        assert score_news_results([result("Company news roundup")])[0] == 0
        assert score_news_results([result("A new office in Austin")])[0] == 1

    def test_news_funding_and_prefix_matching(self):
        score, reasons = score_news_results([result("Acme raised a Series B"), result("Acme launches API")])
        assert score == 5
        assert reasons[0].startswith("Funding signal")
        assert reasons[1].startswith("Growth signal")

    def test_missing_fields_are_tolerated(self):
        assert score_job_results([{"title": None, "snippet": None}]) == (0, [])
        assert score_job_results([]) == (0, [])


class TestCompositeScore:
    @pytest.mark.parametrize(
        "base,signal,expected,rec",
        [
            (10, 10, 10.0, "High priority"),
            (10, 0, 7.0, "High priority"),
            (8, 0, 5.6, "Medium priority"),
            (5, 7, 5.6, "Medium priority"),
            (3, 5, 3.6, "Low priority"),
        ],
    )
    def test_weighting_and_thresholds(self, base, signal, expected, rec):
        out = compute_composite_score(base, signal)
        assert out["composite_score"] == expected
        assert out["recommendation"] == rec


def score_row(domain, composite, rec="High priority"):
    return {"domain": domain, "name": domain.split(".")[0].title(), "composite_score": composite, "recommendation": rec}


class TestCompareRuns:
    def run(self, new_rows, old_rows):
        rows = {"new": new_rows, "old": old_rows}
        with patch.object(diff, "get_run_scores", side_effect=lambda run_id: rows[run_id]):
            return diff.compare_runs("new", "old")

    def test_alert_threshold_is_inclusive_at_one_point(self):
        changes = self.run(
            [score_row("a.com", 8.0), score_row("b.com", 6.5), score_row("c.com", 7.0)],
            [score_row("a.com", 7.0), score_row("b.com", 7.0), score_row("c.com", 7.0)],
        )
        by_domain = {c["domain"]: c for c in changes}
        assert by_domain["a.com"]["alert"] is True
        assert by_domain["a.com"]["type"] == "increase"
        assert by_domain["b.com"]["alert"] is False
        assert by_domain["b.com"]["type"] == "decrease"
        assert "c.com" not in by_domain  # unchanged accounts are omitted

    def test_new_accounts_alert_and_sort_by_magnitude(self):
        changes = self.run(
            [score_row("a.com", 9.0), score_row("b.com", 4.0), score_row("new.com", 6.0)],
            [score_row("a.com", 8.5), score_row("b.com", 7.0)],
        )
        assert [c["domain"] for c in changes] == ["b.com", "a.com", "new.com"]
        new = changes[-1]
        assert new["type"] == "new_account" and new["alert"] is True and new["delta"] is None
