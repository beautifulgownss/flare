"""Pure-logic tests for signal relevance, signal scoring, composite weighting, and score diffs."""
import re
from unittest.mock import patch

import pytest

import diff
from campaign import load_campaign
from score import compute_composite_score
from signals import evaluate_signals, is_relevant, job_query, news_query, score_job_results, score_news_results

SCORING = load_campaign()["scoring"]


def result(title, snippet="", link=None):
    return {"title": title, "snippet": snippet, "link": link}


class TestSignalScoring:
    def test_job_tiers(self):
        score, reasons, evidence = score_job_results([
            result("Acme is hiring a VP of Sales", link="1"),
            result("Account Executive, Mid-Market", link="2"),
            result("Demand Gen Lead", link="3"),
        ])
        assert score == 5  # 3 + 2 + 1 = 6, capped at 5
        assert reasons[0].startswith("Hiring senior sales leader")
        assert reasons[1].startswith("Scaling sales team")
        assert reasons[2].startswith("Growing GTM team")

    def test_one_tier_per_result(self):
        score, reasons, _ = score_job_results([result("VP of Sales and Account Executive roles")])
        assert score == 3
        assert len(reasons) == 1

    def test_acronyms_do_not_match_inside_words(self):
        score, _, _ = score_job_results([result("Engineers across microservices teams")])
        assert score == 0
        score, _, _ = score_job_results([result("Acme names new CRO")])
        assert score == 3

    def test_news_does_not_match_new(self):
        assert score_news_results([result("Company news roundup")])[0] == 0
        assert score_news_results([result("A new office in Austin")])[0] == 1

    def test_news_funding_and_prefix_matching(self):
        score, reasons, _ = score_news_results([result("Acme raised a Series B", link="a"),
                                                result("Acme launches API", link="b")])
        assert score == 5
        assert reasons[0].startswith("Funding signal")
        assert reasons[1].startswith("Growth signal")

    def test_missing_fields_are_tolerated(self):
        assert score_job_results([{"title": None, "snippet": None}]) == (0, [], [])
        assert score_job_results([]) == (0, [], [])

    def test_duplicate_links_count_once(self):
        score, _, _ = score_job_results([result("VP of Sales", link="x"), result("VP of Sales", link="x")])
        assert score == 3

    def test_job_snippets_are_ignored(self):
        # Generic careers pages list every department in the snippet.
        score, _, _ = score_job_results([result("Careers - Retool", "Sales, marketing, VP of Sales, engineering")])
        assert score == 0


class TestRelevance:
    def test_name_collision_is_filtered_out(self):
        # A real false positive from an earlier run: an unrelated "Linear" ad sales job.
        hit = result("Linear Ad Sales jobs in New York", "Linear TV advertising sales roles",
                     "https://www.indeed.com/q-linear-ad-sales-jobs.html")
        assert not is_relevant(hit, "linear.app")
        signals = evaluate_signals({"domain": "linear.app", "name": "Linear"}, [hit], [])
        assert signals["total_signal_score"] == 0
        assert signals["results_considered"] == 1 and signals["results_relevant"] == 0

    def test_company_domain_and_subdomains_are_relevant(self):
        assert is_relevant(result("VP Sales", link="https://linear.app/careers/vp-sales"), "linear.app")
        assert is_relevant(result("VP Sales", link="https://jobs.linear.app/1"), "linear.app")
        assert not is_relevant(result("VP Sales", link="https://notlinear.app/1"), "linear.app")

    def test_ats_board_requires_company_slug(self):
        assert is_relevant(result("AE", link="https://jobs.ashbyhq.com/linear/123"), "linear.app")
        assert is_relevant(result("AE", link="https://boards.greenhouse.io/retool/jobs/9"), "retool.com")
        assert not is_relevant(result("AE", link="https://jobs.ashbyhq.com/other/123"), "linear.app")

    def test_domain_mention_in_text_is_relevant(self):
        assert is_relevant(result("Startup raises Series B", "vercel.com announced funding",
                                  "https://news.example/x"), "vercel.com")

    def test_queries_have_no_hard_coded_years(self):
        for query in (job_query("Stripe", "stripe.com"), news_query("Stripe", "stripe.com")):
            assert not re.search(r"\b20\d\d\b", query)
        assert "stripe.com" in news_query("Stripe", "stripe.com")


class TestCompositeScore:
    @pytest.mark.parametrize(
        "base,signal,expected,rec",
        [
            (10, 10, 10.0, "High priority"),
            (10, 4, 7.0, "High priority"),
            (10, 0, 5.0, "Medium priority"),  # contactability alone is never High
            (8, 0, 4.0, "Low priority"),
            (5, 7, 6.0, "Medium priority"),
        ],
    )
    def test_weighting_and_thresholds(self, base, signal, expected, rec):
        out = compute_composite_score(base, signal, SCORING)
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


class TestAlerts:
    def test_check_and_alert_never_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr(diff, "DIFF_PATH", str(tmp_path / "diff.json"))
        monkeypatch.setattr(diff, "get_last_two_runs", lambda: ("new", "old"))
        rows = {"new": [score_row("a.com", 9.0)], "old": [score_row("a.com", 5.0)]}
        sent = []
        with patch.object(diff, "get_run_scores", side_effect=lambda run_id: rows[run_id]), \
                patch.object(diff, "send_alert", side_effect=lambda alerts, run: sent.append(alerts)):
            output = diff.check_and_alert()
        assert len(output["alerts"]) == 1
        assert len(sent) == 1
        assert (tmp_path / "diff.json").exists()

    def test_slack_preferred_email_fallback(self, monkeypatch):
        monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
        with patch.object(diff, "send_alert_email") as email:
            diff.send_alert([{"type": "new_account", "name": "A", "new_score": 7}], "run_1")
        email.assert_called_once()
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/x")
        with patch.object(diff.session, "post") as post, patch.object(diff, "send_alert_email") as email:
            post.return_value.status_code = 200
            diff.send_alert([{"type": "new_account", "name": "A", "new_score": 7}], "run_1")
        email.assert_not_called()
        assert "Flare" in post.call_args.kwargs["json"]["text"]
