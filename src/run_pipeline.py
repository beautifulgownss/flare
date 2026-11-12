"""Run every pipeline step in order, log the run, and refresh dashboard data."""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from diff import check_and_alert
from tracker import export_runs_json, init_db, log_run

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PUBLIC = ROOT / "dashboard" / "public"

# (display name, script, required). Signals run before scoring so the score,
# the openers, and the sequences all use them. Optional steps depend on
# third-party services (Anthropic, HubSpot) and must never block scoring or the dashboard.
STEPS = [
    ("Enrichment", "src/enrich.py", True),
    ("Signal Fetching", "src/signals.py", True),
    ("Scoring", "src/score.py", True),
    ("Personalization", "src/personalize.py", True),
    ("Sequence Generation", "src/sequence.py", True),
    ("Pitch Page Generation", "src/pitch_pages.py", False),
    ("HubSpot CRM Sync", "src/hubspot_sync.py", False),
    ("HubSpot Contacts Sync", "src/hubspot_contacts_sync.py", False),
]

DASHBOARD_FILES = [
    ("data/enriched/personalized_companies.json", True),
    ("data/sequences/sequences.json", True),
    ("data/scored_final/companies_final.json", True),
    ("data/runs_export.json", True),
    ("data/hubspot_sync_status.json", False),
    ("data/pitch_pages_status.json", False),
]


OUTPUT_DIRS = ["data/enriched", "data/signals", "data/scored_final", "data/sequences", "pages"]
PITCH_STATUS_PATH = "data/pitch_pages_status.json"


def ensure_output_dirs() -> None:
    for rel_path in OUTPUT_DIRS:
        (ROOT / rel_path).mkdir(parents=True, exist_ok=True)


def read_llm_usage(path: Path = ROOT / PITCH_STATUS_PATH) -> dict:
    """Actual token usage recorded by the LLM step, or zeros if it didn't run."""
    try:
        with open(path) as f:
            return json.load(f).get("usage") or {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def banner(text: str) -> None:
    print(f"\n{'=' * 50}\n  {text}\n{'=' * 50}")


def run_step(name: str, script: str, required: bool = True):
    """Run one step as a subprocess. Returns its duration, or None if an optional step failed."""
    banner(f"Running: {name}")
    start = time.time()
    result = subprocess.run([sys.executable, script], cwd=ROOT)
    duration = time.time() - start
    if result.returncode != 0:
        if required:
            print(f"  ERROR: {name} failed (exit {result.returncode})")
            sys.exit(1)
        print(f"  WARNING: {name} failed. Continuing, since this step is optional.")
        return None
    print(f"  Completed in {duration:.2f}s")
    return duration


def copy_dashboard_files() -> None:
    DASHBOARD_PUBLIC.mkdir(parents=True, exist_ok=True)
    for rel_path, required in DASHBOARD_FILES:
        src = ROOT / rel_path
        if src.exists():
            shutil.copy2(src, DASHBOARD_PUBLIC / src.name)
        elif required:
            print(f"  WARNING: expected output missing: {rel_path}")
    pages = ROOT / "pages"
    if pages.is_dir():
        dest = DASHBOARD_PUBLIC / "pages"
        dest.mkdir(exist_ok=True)
        for page in pages.glob("*.html"):
            shutil.copy2(page, dest / page.name)


def main():
    os.chdir(ROOT)
    banner("FLARE PIPELINE: FULL RUN")
    ensure_output_dirs()
    run_id = f"run_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    print(f"\n  Run ID: {run_id}")

    pipeline_start = time.time()
    for name, script, required in STEPS:
        run_step(name, script, required)
    total_duration = time.time() - pipeline_start

    with open("data/scored_final/companies_final.json") as f:
        companies = json.load(f)

    init_db()
    log_run(run_id=run_id, companies=companies, duration=total_duration, notes="Full pipeline run",
            llm_usage=read_llm_usage())
    banner("Score change check")
    check_and_alert()
    export_runs_json("data/runs_export.json")
    copy_dashboard_files()

    banner("PIPELINE COMPLETE")
    print(f"  Run ID: {run_id}")
    print(f"  Duration: {total_duration:.2f}s")
    print(f"  Companies processed: {len(companies)}")
    print("  Dashboard files updated\n")


if __name__ == "__main__":
    main()
