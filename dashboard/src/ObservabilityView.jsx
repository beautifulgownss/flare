import { Card, Badge } from "./hockney/components";

function MetricCard({ label, value, sub }) {
  return (
    <Card padding="var(--space-4)" style={{ flex: 1 }}>
      <p className="splash-kicker" style={{ margin: "0 0 6px" }}>{label}</p>
      <p style={{ font: "var(--type-h2)", margin: 0 }}>{value}</p>
      {sub && <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: "2px 0 0", fontSize: 11 }}>{sub}</p>}
    </Card>
  );
}

function RunRow({ run, isLatest }) {
  const date = new Date(run.timestamp + "Z");
  const formatted = date.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
    " · " + date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  return (
    <div style={{
      background: isLatest ? "var(--paper)" : "transparent",
      border: `var(--border-base) solid ${isLatest ? "var(--ink)" : "var(--canvas-deep)"}`,
      padding: "var(--space-3)",
      marginBottom: "var(--space-2)",
      display: "grid",
      gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr",
      alignItems: "center",
      gap: 8,
    }}>
      <div>
        <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: "0 0 2px" }}>{run.run_id}</p>
        <p style={{ font: "var(--type-small)", color: "var(--text-muted)", margin: 0, fontSize: 11 }}>{formatted}</p>
      </div>
      <p style={{ font: "var(--type-small)", margin: 0, textAlign: "center" }}>{run.companies_processed}</p>
      <p style={{ font: "var(--type-small)", color: "var(--coral)", margin: 0, textAlign: "center" }}>{run.high_priority}</p>
      <p style={{ font: "var(--type-small)", color: "var(--pool-blue)", margin: 0, textAlign: "center" }}>{run.medium_priority}</p>
      <p style={{ font: "var(--type-small)", color: "var(--lawn)", margin: 0, textAlign: "center" }}>{run.avg_composite_score}</p>
      <div style={{ textAlign: "right" }}>
        <p style={{ font: "var(--type-small)", margin: "0 0 2px" }}>{run.duration_seconds}s</p>
        <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0, fontSize: 11 }}>${run.estimated_token_cost}</p>
      </div>
    </div>
  );
}

function ScoreTable({ run }) {
  if (!run?.scores?.length) return null;
  return (
    <div>
      {run.scores.map((s, i) => (
        <div key={i} style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "var(--space-2) 0", borderBottom: "var(--border-hairline) solid var(--canvas-deep)"
        }}>
          <div>
            <span style={{ font: "var(--type-small)", marginRight: 8 }}>{s.name}</span>
            <span style={{ font: "var(--type-mono)", color: "var(--text-muted)", fontSize: 11 }}>{s.domain}</span>
          </div>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>base <span style={{ color: "var(--pool-blue)" }}>{s.base_score}</span></span>
            <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>signal <span style={{ color: "var(--coral)" }}>{s.signal_score}</span></span>
            <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>composite <span style={{ color: "var(--lawn)", fontWeight: "var(--weight-semibold)" }}>{s.composite_score}</span></span>
            <Badge variant={s.recommendation === "High priority" ? "high" : s.recommendation === "Medium priority" ? "medium" : "low"}>
              {s.recommendation}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ObservabilityView({ runs }) {
  if (!runs.length) {
    return <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "var(--space-6)" }}>No runs logged yet.</p>;
  }

  const latest = runs[0];
  const totalRuns = runs.length;
  const avgDuration = (runs.reduce((a, r) => a + r.duration_seconds, 0) / runs.length).toFixed(1);
  const totalCost = runs.reduce((a, r) => a + r.estimated_token_cost, 0).toFixed(4);

  return (
    <div>
      <div style={{ borderBottom: "var(--border-base) solid var(--ink)", paddingBottom: "var(--space-4)", marginBottom: "var(--space-5)" }}>
        <p className="splash-kicker" style={{ margin: "0 0 4px" }}>pipeline observability · run history</p>
        <h1 style={{ font: "var(--type-h1)", margin: "0 0 var(--space-4)" }}>Run history</h1>
        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <MetricCard label="Total runs" value={totalRuns} />
          <MetricCard label="Avg duration" value={`${avgDuration}s`} />
          <MetricCard label="Total est. cost" value={`$${totalCost}`} sub="mock pricing" />
          <MetricCard label="Last run" value={latest.companies_processed} sub="companies processed" />
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr",
        gap: 8, padding: "0 var(--space-3)",
        marginBottom: "var(--space-2)"
      }}>
        {["Run ID", "Total", "High", "Medium", "Avg score", "Duration / Cost"].map(h => (
          <p key={h} className="splash-kicker" style={{ margin: 0, textAlign: h === "Duration / Cost" ? "right" : h === "Run ID" ? "left" : "center" }}>{h}</p>
        ))}
      </div>

      {runs.map((run, i) => (
        <RunRow key={run.run_id} run={run} isLatest={i === 0} />
      ))}

      <div style={{ marginTop: "var(--space-6)" }}>
        <p style={{ font: "var(--type-h3)", margin: "0 0 var(--space-3)" }}>
          Latest run · {latest.run_id}
        </p>
        <Card>
          <ScoreTable run={latest} />
        </Card>
      </div>
    </div>
  );
}
