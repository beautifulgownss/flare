import json
import os
import sqlite3
from tracker import get_runs, get_run_scores

DB_PATH = "data/runs.db"


def get_last_two_runs() -> tuple:
    """Returns the two most recent run IDs."""
    runs = get_runs(limit=2)
    if len(runs) < 2:
        print("Not enough runs to compare — need at least 2.")
        return None, None
    return runs[0]["run_id"], runs[1]["run_id"]


def compare_runs(run_id_new: str, run_id_old: str) -> list:
    """Compares scores between two runs and returns changes."""
    new_scores = {s["domain"]: s for s in get_run_scores(run_id_new)}
    old_scores = {s["domain"]: s for s in get_run_scores(run_id_old)}

    changes = []
    for domain, new in new_scores.items():
        old = old_scores.get(domain)
        if not old:
            changes.append({
                "domain": domain,
                "name": new["name"],
                "type": "new_account",
                "old_score": None,
                "new_score": new["composite_score"],
                "delta": None,
                "alert": True,
            })
            continue

        delta = round(new["composite_score"] - old["composite_score"], 2)
        alert = abs(delta) >= 1.0

        if delta != 0:
            changes.append({
                "domain": domain,
                "name": new["name"],
                "type": "increase" if delta > 0 else "decrease",
                "old_score": old["composite_score"],
                "new_score": new["composite_score"],
                "delta": delta,
                "old_recommendation": old["recommendation"],
                "new_recommendation": new["recommendation"],
                "alert": alert,
            })

    return sorted(changes, key=lambda x: abs(x.get("delta") or 0), reverse=True)


def print_summary(changes: list, run_id_new: str, run_id_old: str):
    print(f"\n{'='*50}")
    print(f"  SCORE CHANGE REPORT")
    print(f"  New run:  {run_id_new}")
    print(f"  Old run:  {run_id_old}")
    print(f"{'='*50}")

    if not changes:
        print("\n  No score changes detected.")
        return

    alerts = [c for c in changes if c.get("alert")]
    if alerts:
        print(f"\n  🚨 ALERTS — {len(alerts)} significant changes (±1.0+):")
        for c in alerts:
            arrow = "↑" if c["type"] == "increase" else "↓" if c["type"] == "decrease" else "★"
            print(f"    {arrow} {c['name']} ({c['domain']})")
            if c["type"] == "new_account":
                print(f"       New account detected — score: {c['new_score']}")
            else:
                print(f"       {c['old_score']} → {c['new_score']} ({'+' if c['delta'] > 0 else ''}{c['delta']})")
                if c["old_recommendation"] != c["new_recommendation"]:
                    print(f"       Priority changed: {c['old_recommendation']} → {c['new_recommendation']}")

    minor = [c for c in changes if not c.get("alert")]
    if minor:
        print(f"\n  Minor changes (< 1.0 delta):")
        for c in minor:
            print(f"    {c['name']}: {c['old_score']} → {c['new_score']} ({'+' if c['delta'] > 0 else ''}{c['delta']})")

    print(f"\n  Total changes: {len(changes)} | Alerts: {len(alerts)}")
    print(f"{'='*50}\n")

    # Exit with code 1 if there are alerts — GitHub Actions will flag the run
    if alerts:
        print("  Score alerts detected — flagging run.")
        exit(1)


def main():
    run_id_new, run_id_old = get_last_two_runs()
    if not run_id_new:
        return

    changes = compare_runs(run_id_new, run_id_old)
    print_summary(changes, run_id_new, run_id_old)

    # Save diff output
    output = {
        "run_id_new": run_id_new,
        "run_id_old": run_id_old,
        "changes": changes,
        "alerts": [c for c in changes if c.get("alert")]
    }
    with open("data/score_diff.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Diff saved to data/score_diff.json")


if __name__ == "__main__":
    main()