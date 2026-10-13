import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from demo import run_demo, render_report
from campaign import load_campaign


class DemoTests(unittest.TestCase):
    def test_offline_end_to_end_and_repeatable(self):
        with tempfile.TemporaryDirectory() as directory, patch("socket.socket", side_effect=AssertionError("Network forbidden")):
            destination, payload = run_demo(output_dir=directory)
            first_report = (destination / "index.html").read_text()
            first_json = (destination / "results.json").read_text()
            self.assertEqual(len(payload["accounts"]), 4)
            drafts = [a for a in payload["accounts"] if a["outreach"]["sequence"]]
            self.assertEqual(len(drafts), 2)
            self.assertTrue(all(len(a["outreach"]["sequence"]) == 3 for a in drafts))
            self.assertEqual(payload["accounts"][1]["best_contact"]["email"], "jordan@cedar-metrics.example")
            self.assertIn("fictional", first_report)
            self.assertEqual(json.loads(first_json)["mode"], "offline_demo")
            run_demo(output_dir=directory)
            self.assertEqual(first_json, (destination / "results.json").read_text())
            self.assertEqual(first_report, (destination / "index.html").read_text())

    def test_report_escapes_untrusted_content(self):
        with tempfile.TemporaryDirectory() as directory:
            _, payload = run_demo(output_dir=directory)
            payload["accounts"][0]["name"] = '<script>alert("x")</script>'
            report = render_report(payload["accounts"], load_campaign()["offer"])
            self.assertNotIn("<script>", report)
            self.assertIn("&lt;script&gt;", report)


if __name__ == "__main__":
    unittest.main()
