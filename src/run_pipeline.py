import json
import time
import uuid
import subprocess
import sys
import os
from datetime import datetime
from tracker import init_db, log_run, export_runs_json
def run_step(name: str, script: str):
    print(f"\n{'='*50}")
    print(f"  Running: {name}")
    print(f"{'='*50}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    duration = time.time() - start
    if result.returncode != 0:
        print(f"  ERROR: {name} failed")
        sys.exit(1)
    print(f"  Completed in {round(duration, 2)}s")
    return duration
def run_step_optional(name: str, script: str):
    """Like run_step, but failure doesn't stop the pipeline."""
    print(f"\n{'='*50}")
    print(f"  Running: {name}")
    print(f"{'='*50}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    duration = time.time() - start
    if result.returncode != 0:
        print(f"  WARNING: {name} failed — continuing pipeline anyway")
        return None
    print(f"  Completed in {round(duration, 2)}s")
    return duration
def main():
    print("\n" + "="*50)
    print("  GTM ENRICHMENT PIPELINE — FULL RUN")
    print("="*50)
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
    print(f"\n  Run ID: {run_id}")
    pipeline_start = time.time()
    # Run all pipeline steps
    run_step("Enrichment", "src/enrich.py")
    run_step("Scoring", "src/score.py")
    run_step("Personalization", "src/personalize.py")
    run_step("Sequence Generation", "src/sequence.py")
    run_step("Signal Fetching", "src/signals.py")
    # HubSpot sync — non-fatal, pipeline continues even if this fails
    run_step_optional("HubSpot CRM Sync", "src/hubspot_sync.py")
    run_step_optional("HubSpot Contacts Sync", "src/hubspot_contacts_sync.py")
    total_duration = time.time() - pipeline_start
    # Load final output for logging
    with open("data/scored_final/companies_final.json", "r") as f:
        companies = json.load(f)
    # Initialize DB and log run
    init_db()
    log_run(
        run_id=run_id,
        companies=companies,
        duration=total_duration,
        notes="Full pipeline run"
    )
    # Export runs to JSON for dashboard
    export_runs_json("data/runs_export.json")
    # Copy outputs to dashboard public folder
    os.system("cp data/enriched/personalized_companies.json dashboard/public/")
    os.system("cp data/sequences/sequences.json dashboard/public/")
    os.system("cp data/scored_final/companies_final.json dashboard/public/")
    os.system("cp data/runs_export.json dashboard/public/")
    print(f"\n{'='*50}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Run ID: {run_id}")
    print(f"  Duration: {round(total_duration, 2)}s")
    print(f"  Companies processed: {len(companies)}")
    print(f"  Dashboard files updated")
    print(f"{'='*50}\n")
if __name__ == "__main__":
    main()
