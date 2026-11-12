"""Compare the last two runs and alert on meaningful score changes (Slack, then email)."""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from http_client import session
from tracker import get_run_scores, get_runs

load_dotenv()

DIFF_PATH = "data/score_diff.json"


def get_last_two_runs() -> tuple:
    runs = get_runs(limit=2)
    if len(runs) < 2:
        print("Not enough runs to compare — need at least 2.")
        return None, None
    return runs[0]["run_id"], runs[1]["run_id"]


def compare_runs(run_id_new: str, run_id_old: str) -> list:
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


def format_slack_message(alerts: list, run_id_new: str) -> dict:
    lines = [f"*Flare: {len(alerts)} account score change(s)* (run `{run_id_new}`)"]
    for a in alerts:
        if a["type"] == "new_account":
            lines.append(f"- {a['name']}: new account, score {a['new_score']}")
        else:
            sign = "+" if a["delta"] > 0 else ""
            line = f"- {a['name']}: {a['old_score']} -> {a['new_score']} ({sign}{a['delta']})"
            if a.get("old_recommendation") != a.get("new_recommendation"):
                line += f", {a['old_recommendation']} -> {a['new_recommendation']}"
            lines.append(line)
    return {"text": "\n".join(lines)}


def send_slack_alert(alerts: list, run_id_new: str) -> bool:
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return False
    response = session.post(webhook, json=format_slack_message(alerts, run_id_new))
    if response.status_code == 200:
        print("  Slack alert sent")
        return True
    print(f"  Slack alert failed: {response.status_code}")
    return False


def send_alert(alerts: list, run_id_new: str) -> None:
    """Prefer Slack; fall back to email if Slack isn't configured or fails."""
    if not send_slack_alert(alerts, run_id_new):
        send_alert_email(alerts, run_id_new)


def send_alert_email(alerts: list, run_id_new: str):
    sender = os.getenv("ALERT_EMAIL_SENDER")
    password = os.getenv("ALERT_EMAIL_PASSWORD")
    recipient = os.getenv("ALERT_EMAIL_RECIPIENT")

    if not sender or not password or not recipient:
        print("  No Slack webhook or email alert settings configured; skipping alert.")
        return

    subject = f"Flare Alert — {len(alerts)} score change(s) detected"

    rows = ""
    for a in alerts:
        if a["type"] == "new_account":
            rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">{a['name']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">—</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">{a['new_score']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;color:#F59E0B;">New account</td>
            </tr>"""
        else:
            delta_color = "#22C55E" if a["delta"] > 0 else "#EF4444"
            delta_str = f"+{a['delta']}" if a["delta"] > 0 else str(a["delta"])
            priority_change = ""
            if a.get("old_recommendation") != a.get("new_recommendation"):
                priority_change = f"<br><small style='color:#64748B'>{a['old_recommendation']} → {a['new_recommendation']}</small>"
            rows += f"""
            <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">{a['name']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">{a['old_score']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;">{a['new_score']}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #1E293B;color:{delta_color};">{delta_str}{priority_change}</td>
            </tr>"""

    body = f"""
    <html>
    <body style="font-family:Inter,sans-serif;background:#0A0F1E;color:#F0F4FF;padding:2rem;">
        <div style="max-width:600px;margin:0 auto;">
            <p style="font-family:monospace;font-size:12px;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;">
                Flare · Score Alert
            </p>
            <h1 style="font-size:22px;font-weight:500;margin:0 0 1rem;">
                {len(alerts)} score change(s) detected
            </h1>
            <p style="color:#64748B;font-size:14px;">Run ID: <span style="font-family:monospace;">{run_id_new}</span></p>

            <table style="width:100%;border-collapse:collapse;margin-top:1.5rem;background:#111827;border-radius:8px;overflow:hidden;">
                <thead>
                    <tr style="background:#1E293B;">
                        <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Company</th>
                        <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Old score</th>
                        <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">New score</th>
                        <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748B;font-weight:500;">Change</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <p style="margin-top:1.5rem;font-size:13px;color:#64748B;">
                View full run history in your
                <a href="http://localhost:3000" style="color:#378ADD;">Flare dashboard</a>.
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print(f"  Alert email sent to {recipient}")
    except Exception as e:
        print(f"  Failed to send alert email: {e}")


def print_summary(changes: list, run_id_new: str, run_id_old: str):
    print(f"\n{'='*50}")
    print("  SCORE CHANGE REPORT")
    print(f"  New run:  {run_id_new}")
    print(f"  Old run:  {run_id_old}")
    print(f"{'='*50}")

    if not changes:
        print("\n  No score changes detected.")
        return

    alerts = [c for c in changes if c.get("alert")]
    if alerts:
        print(f"\n  ALERTS — {len(alerts)} significant changes:")
        for c in alerts:
            arrow = "up" if c["type"] == "increase" else "down" if c["type"] == "decrease" else "new"
            print(f"    {arrow} {c['name']} ({c['domain']})")
            if c["type"] == "new_account":
                print(f"       New account — score: {c['new_score']}")
            else:
                print(f"       {c['old_score']} → {c['new_score']} ({'+' if c['delta'] > 0 else ''}{c['delta']})")
                if c["old_recommendation"] != c["new_recommendation"]:
                    print(f"       Priority: {c['old_recommendation']} → {c['new_recommendation']}")

        send_alert(alerts, run_id_new)

    minor = [c for c in changes if not c.get("alert")]
    if minor:
        print("\n  Minor changes (< 1.0 delta):")
        for c in minor:
            print(f"    {c['name']}: {c['old_score']} → {c['new_score']} ({'+' if c['delta'] > 0 else ''}{c['delta']})")

    print(f"\n  Total changes: {len(changes)} | Alerts: {len(alerts)}")
    print(f"{'='*50}\n")


def check_and_alert() -> dict | None:
    """Run from run_pipeline.py after the run is logged. Alerts never fail the run."""
    run_id_new, run_id_old = get_last_two_runs()
    if not run_id_new:
        return None

    changes = compare_runs(run_id_new, run_id_old)
    print_summary(changes, run_id_new, run_id_old)

    output = {
        "run_id_new": run_id_new,
        "run_id_old": run_id_old,
        "changes": changes,
        "alerts": [c for c in changes if c.get("alert")]
    }
    with open(DIFF_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Diff saved to {DIFF_PATH}")
    return output


if __name__ == "__main__":
    check_and_alert()
