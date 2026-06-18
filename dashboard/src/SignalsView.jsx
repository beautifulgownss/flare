import { useState } from "react";

const COLORS = {
  bg: "#0A0F1E",
  card: "#111827",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  high: "#378ADD",
  innerBg: "#0A0F1E",
  amber: "#F59E0B",
  green: "#22C55E",
};

function ScoreBar({ label, score, max = 10, color }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 12, color: COLORS.muted }}>{label}</span>
        <span style={{ fontSize: 12, fontFamily: "monospace", fontWeight: 500, color: COLORS.text }}>{score}/{max}</span>
      </div>
      <div style={{ height: 4, background: "#1E293B", borderRadius: 2, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${(score / max) * 100}%`,
          background: color, borderRadius: 2,
          transition: "width 1s ease"
        }} />
      </div>
    </div>
  );
}

function SignalTag({ text, type }) {
  const colors = {
    job: { bg: "#0C447C", color: "#85B7EB" },
    news: { bg: "#633806", color: "#F59E0B" },
  };
  const c = colors[type] || colors.job;
  return (
    <div style={{
      background: c.bg, borderRadius: 6, padding: "6px 10px",
      marginBottom: 6, fontSize: 12, color: c.color, lineHeight: 1.5
    }}>
      {text}
    </div>
  );
}

function CompanySignalCard({ company }) {
  const [expanded, setExpanded] = useState(false);
  const isHigh = company.final_recommendation === "High priority";
  const isMed = company.final_recommendation === "Medium priority";

  const accentColor = isHigh ? COLORS.high : isMed ? COLORS.amber : COLORS.muted;

  return (
    <div style={{
      background: COLORS.card,
      border: `0.5px solid ${COLORS.border}`,
      borderLeft: `3px solid ${accentColor}`,
      borderRadius: 12,
      padding: "1rem 1.25rem",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
        <div>
          <p style={{ fontSize: 16, fontWeight: 500, color: COLORS.text, margin: "0 0 2px" }}>{company.name}</p>
          <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: 0 }}>{company.domain}</p>
        </div>
        <span style={{
          fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 500,
          background: isHigh ? "#0C447C" : isMed ? "#633806" : "#1E293B",
          color: isHigh ? "#85B7EB" : isMed ? COLORS.amber : COLORS.muted,
        }}>
          {company.final_recommendation}
        </span>
      </div>

      <ScoreBar label="Base score" score={company.score} color={COLORS.high} />
      <ScoreBar label="Signal score" score={company.total_signal_score} max={10} color={COLORS.amber} />
      <div style={{ borderTop: `0.5px solid ${COLORS.border}`, margin: "10px 0" }} />
      <ScoreBar label="Composite score" score={company.composite_score} color={COLORS.green} />

      {(company.job_reasons?.length > 0 || company.news_reasons?.length > 0) && (
        <>
          <div style={{ borderTop: `0.5px solid ${COLORS.border}`, margin: "12px 0" }} />
          <div
            onClick={() => setExpanded(!expanded)}
            style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer", marginBottom: expanded ? 10 : 0 }}
          >
            <span style={{ fontSize: 12, color: COLORS.muted }}>
              {(company.job_reasons?.length || 0) + (company.news_reasons?.length || 0)} signals detected
            </span>
            <span style={{ fontSize: 12, color: COLORS.muted }}>{expanded ? "▲" : "▼"}</span>
          </div>

          {expanded && (
            <div>
              {company.job_reasons?.map((r, i) => (
                <SignalTag key={i} text={r} type="job" />
              ))}
              {company.news_reasons?.map((r, i) => (
                <SignalTag key={i} text={r} type="news" />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function SignalsView({ companies }) {
  if (!companies.length) {
    return <p style={{ color: COLORS.muted, textAlign: "center", padding: "2rem" }}>Loading signals...</p>;
  }

  const high = companies.filter(c => c.final_recommendation === "High priority").length;
  const med = companies.filter(c => c.final_recommendation === "Medium priority").length;
  const avgComposite = (companies.reduce((a, c) => a + (c.composite_score || 0), 0) / companies.length).toFixed(1);

  return (
    <div>
      <div style={{ borderBottom: `0.5px solid ${COLORS.border}`, paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          lead scoring · live signals
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 1rem", color: COLORS.text }}>Signal-weighted scoring</h1>
        <div style={{ display: "flex", gap: 12 }}>
          {[
            { label: "High priority", value: high },
            { label: "Medium priority", value: med },
            { label: "Avg composite score", value: avgComposite },
            { label: "Signal sources", value: "Jobs + News" },
          ].map((s) => (
            <div key={s.label} style={{ background: "#111827", borderRadius: 8, padding: "0.75rem 1rem", flex: 1 }}>
              <p style={{ fontSize: 12, color: COLORS.muted, margin: "0 0 2px" }}>{s.label}</p>
              <p style={{ fontSize: 20, fontWeight: 500, color: COLORS.text, margin: 0 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 12 }}>
        {companies.map((c) => <CompanySignalCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}