import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/runs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            companies_processed INTEGER,
            high_priority INTEGER,
            medium_priority INTEGER,
            low_priority INTEGER,
            avg_composite_score REAL,
            estimated_token_cost REAL,
            duration_seconds REAL,
            notes TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS run_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            domain TEXT NOT NULL,
            name TEXT NOT NULL,
            base_score REAL,
            signal_score REAL,
            composite_score REAL,
            recommendation TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_run(run_id: str, companies: list, duration: float, notes: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    high = sum(1 for co in companies if co.get("final_recommendation") == "High priority")
    medium = sum(1 for co in companies if co.get("final_recommendation") == "Medium priority")
    low = sum(1 for co in companies if co.get("final_recommendation") == "Low priority")
    avg_score = round(
        sum(co.get("composite_score", 0) for co in companies) / len(companies), 2
    ) if companies else 0

    # Estimate token cost — mock at $0.002 per company (gpt-4o-mini rate)
    estimated_cost = round(len(companies) * 0.002, 4)

    c.execute("""
        INSERT INTO runs (run_id, timestamp, companies_processed, high_priority,
        medium_priority, low_priority, avg_composite_score, estimated_token_cost,
        duration_seconds, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        datetime.utcnow().isoformat(),
        len(companies),
        high, medium, low,
        avg_score,
        estimated_cost,
        round(duration, 2),
        notes
    ))

    for co in companies:
        c.execute("""
            INSERT INTO run_scores (run_id, domain, name, base_score,
            signal_score, composite_score, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            co.get("domain"),
            co.get("name"),
            co.get("score"),
            co.get("total_signal_score"),
            co.get("composite_score"),
            co.get("final_recommendation"),
        ))

    conn.commit()
    conn.close()
    print(f"  Run {run_id} logged to database")


def get_runs(limit: int = 10) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM runs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_run_scores(run_id: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM run_scores WHERE run_id = ?", (run_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def export_runs_json(output_path: str = "data/runs_export.json"):
    runs = get_runs(limit=50)
    for run in runs:
        run["scores"] = get_run_scores(run["run_id"])
    with open(output_path, "w") as f:
        json.dump(runs, f, indent=2)
    print(f"  Runs exported to {output_path}")