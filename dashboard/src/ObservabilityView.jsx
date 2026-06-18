const COLORS = {
  bg: "#0A0F1E",
  card: "#111827",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  high: "#378ADD",
  amber: "#F59E0B",
  green: "#22C55E",
  innerBg: "#0A0F1E",
};

function MetricCard({ label, value, sub }) {
  return (
    <div style={{ background: "#111827", borderRadius: 8, padding: "0.75rem 1rem", flex: 1 }}>
      <p style={{ fontSize: 12, color: COLORS.muted, margin: "0 0 2px" }}>{label}</p>
      <p style={{ fontSize: 20, fontWeight: 500, color: COLORS.text, margin: 0 }}>{value}</p>
      {sub && <p style={{ fontSize: 11, color: COLORS.muted, margin: "2px 0 0", fontFamily: "monospace" }}>{sub}</p>}
    </div>
  );
}

function RunRow({ run, isLatest }) {
  const date = new Date(run.timestamp + "Z");
  const formatted = date.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
    " · " + date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  return (
    <div style={{
      background: isLatest ? COLORS.card : "transparent",
      border: `0.5px solid ${isLatest ? COLORS.high : COLORS.border}`,
      borderRadius: 10,
      padding: "0.875rem 1rem",
      marginBottom: 8,
      display: "grid",
      gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr",
      alignItems: "center",
      gap: 8,
    }}>
      <div>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 2px" }}>{run.run_id}</p>
        <p style={{ fontSize: 11, color: COLORS.muted, margin: 0 }}>{formatted}</p>
      </div>
      <p style={{ fontSize: 13, color: COLORS.text, margin: 0, textAlign: "center" }}>{run.companies_processed}</p>
      <p style={{ fontSize: 13, color: "#85B7EB", margin: 0, textAlign: "center" }}>{run.high_priority}</p>
      <p style={{ fontSize: 13, color: COLORS.amber, margin: 0, textAlign: "center" }}>{run.medium_priority}</p>
      <p style={{ fontSize: 13, color: COLORS.green, margin: 0, textAlign: "center" }}>{run.avg_composite_score}</p>
      <div style={{ textAlign: "right" }}>
        <p style={{ fontSize: 13, color: COLORS.text, margin: "0 0 2px" }}>{run.duration_seconds}s</p>
        <p style={{ fontSize: 11, color: COLORS.muted, margin: 0 }}>${run.estimated_token_cost}</p>
      </div>
    </div>
  );
}

function ScoreTable({ run }) {
  if (!run?.scores?.length) return null;
  return (
    <div style={{ marginTop: 8 }}>
      {run.scores.map((s, i) => (
        <div key={i} style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "6px 0", borderBottom: `0.5px solid ${COLORS.border}`
        }}>
          <div>
            <span style={{ fontSize: 13, color: COLORS.text, marginRight: 8 }}>{s.name}</span>
            <span style={{ fontSize: 11, fontFamily: "monospace", color: COLORS.muted }}>{s.domain}</span>
          </div>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <span style={{ fontSize: 12, color: COLORS.muted }}>base <span style={{ color: COLORS.high }}>{s.base_score}</span></span>
            <span style={{ fontSize: 12, color: COLORS.muted }}>signal <span style={{ color: COLORS.amber }}>{s.signal_score}</span></span>
            <span style={{ fontSize: 12, color: COLORS.muted }}>composite <span style={{ color: COLORS.green, fontWeight: 500 }}>{s.composite_score}</span></span>
            <span style={{
              fontSize: 11, padding: "2px 8px", borderRadius: 4,
              background: s.recommendation === "High priority" ? "#0C447C" : s.recommendation === "Medium priority" ? "#633806" : "#1E293B",
              color: s.recommendation === "High priority" ? "#85B7EB" : s.recommendation === "Medium priority" ? COLORS.amber : COLORS.muted,
            }}>{s.recommendation}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ObservabilityView({ runs }) {
  if (!runs.length) {
    return <p style={{ color: COLORS.muted, textAlign: "center", padding: "2rem" }}>No runs logged yet.</p>;
  }

  const latest = runs[0];
  const totalRuns = runs.length;
  const avgDuration = (runs.reduce((a, r) => a + r.duration_seconds, 0) / runs.length).toFixed(1);
  const totalCost = runs.reduce((a, r) => a + r.estimated_token_cost, 0).toFixed(4);

  return (
    <div>
      <div style={{ borderBottom: `0.5px solid ${COLORS.border}`, paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          pipeline observability · run history
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 1rem", color: COLORS.text }}>Run history</h1>
        <div style={{ display: "flex", gap: 12 }}>
          <MetricCard label="Total runs" value={totalRuns} />
          <MetricCard label="Avg duration" value={`${avgDuration}s`} />
          <MetricCard label="Total est. cost" value={`$${totalCost}`} sub="mock pricing" />
          <MetricCard label="Last run" value={latest.companies_processed} sub="companies processed" />
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr 1fr",
        gap: 8, padding: "0 1rem",
        marginBottom: 8
      }}>
        {["Run ID", "Total", "High", "Medium", "Avg score", "Duration / Cost"].map(h => (
          <p key={h} style={{ fontSize: 11, color: COLORS.muted, margin: 0, textTransform: "uppercase", letterSpacing: "0.04em", textAlign: h === "Duration / Cost" ? "right" : h === "Run ID" ? "left" : "center" }}>{h}</p>
        ))}
      </div>

      {runs.map((run, i) => (
        <RunRow key={run.run_id} run={run} isLatest={i === 0} />
      ))}

      <div style={{ marginTop: "1.5rem" }}>
        <p style={{ fontSize: 13, fontWeight: 500, color: COLORS.text, margin: "0 0 12px" }}>
          Latest run · {latest.run_id}
        </p>
        <div style={{
          background: COLORS.card, border: `0.5px solid ${COLORS.border}`,
          borderRadius: 10, padding: "1rem 1.25rem"
        }}>
          <ScoreTable run={latest} />
        </div>
      </div>
    </div>
  );
}