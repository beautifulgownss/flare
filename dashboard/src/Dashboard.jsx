import { useState, useEffect } from "react";

const COLORS = {
  high: "#378ADD",
  low: "#888780",
  bg: "#0A0F1E",
  card: "#111827",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  amber: "#F59E0B",
};

function initials(name) {
  if (!name) return "?";
  return name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
}

function ScoreMeter({ score }) {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    setTimeout(() => setWidth((score / 10) * 100), 100);
  }, [score]);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "12px 0" }}>
      <div style={{ flex: 1, height: 4, background: "#1E293B", borderRadius: 2, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${width}%`, background: score >= 6 ? COLORS.high : COLORS.low, borderRadius: 2, transition: "width 1s ease" }} />
      </div>
      <span style={{ fontFamily: "monospace", fontSize: 13, fontWeight: 500, color: COLORS.text, minWidth: 36 }}>
        {score}/10
      </span>
    </div>
  );
}

function CompanyCard({ company }) {
  const isHigh = company.recommendation === "High priority";

  return (
    <div style={{
      background: COLORS.card,
      border: `0.5px solid ${COLORS.border}`,
      borderLeft: isHigh ? `3px solid ${COLORS.high}` : `0.5px solid ${COLORS.border}`,
      borderRadius: 12,
      padding: "1rem 1.25rem",
      opacity: isHigh ? 1 : 0.6,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
        <div>
          <p style={{ fontSize: 16, fontWeight: 500, color: COLORS.text, margin: "0 0 2px" }}>{company.name}</p>
          <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: 0 }}>{company.domain}</p>
        </div>
        <span style={{
          fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 500,
          background: isHigh ? "#0C447C" : "#1E293B",
          color: isHigh ? "#85B7EB" : COLORS.muted,
        }}>
          {company.recommendation}
        </span>
      </div>

      <ScoreMeter score={company.score} />

      <p style={{ fontSize: 11, color: COLORS.muted, margin: "0 0 12px", display: "flex", alignItems: "center", gap: 4 }}>
        ✉ {company.emails_found ?? "—"} emails found
      </p>

      {isHigh && company.best_contact_name ? (
        <>
          <div style={{ borderTop: `0.5px solid ${COLORS.border}`, margin: "12px 0" }} />
          <div style={{ display: "flex", gap: 10, marginBottom: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%",
              background: "#0C447C", display: "flex", alignItems: "center",
              justifyContent: "center", fontSize: 11, fontWeight: 500,
              color: "#85B7EB", flexShrink: 0,
            }}>
              {initials(company.best_contact_name)}
            </div>
            <div>
              <p style={{ fontSize: 13, fontWeight: 500, color: COLORS.text, margin: "0 0 1px" }}>{company.best_contact_name}</p>
              <p style={{ fontSize: 12, color: COLORS.muted, margin: "0 0 1px" }}>{company.best_contact_title}</p>
              <p style={{ fontSize: 11, fontFamily: "monospace", color: COLORS.high, margin: 0 }}>{company.best_contact_email}</p>
            </div>
          </div>
          <div style={{ background: "#0A0F1E", borderRadius: 8, padding: "10px 12px" }}>
            <p style={{ fontSize: 11, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.04em" }}>opener</p>
            <p style={{ fontSize: 13, color: COLORS.text, margin: 0, lineHeight: 1.6 }}>{company.opener}</p>
          </div>
        </>
      ) : (
        <p style={{ fontSize: 13, color: COLORS.muted, fontStyle: "italic", textAlign: "center", padding: "1rem 0" }}>
          No contacts found — low discoverability
        </p>
      )}
    </div>
  );
}

export default function Dashboard({ companies = [] }) {
  const high = companies.filter((c) => c.recommendation === "High priority").length;
  const avgScore = companies.length
    ? (companies.reduce((a, c) => a + c.score, 0) / companies.length).toFixed(1)
    : 0;

  return (
    <div>
      <div style={{ borderBottom: `0.5px solid #1E293B`, paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: "#64748B", margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          GTM enrichment pipeline · run output
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 1rem" }}>Account prioritization</h1>
        <div style={{ display: "flex", gap: 12 }}>
          {[
            { label: "Companies enriched", value: companies.length },
            { label: "High priority", value: high },
            { label: "Openers generated", value: high },
            { label: "Avg score", value: avgScore },
          ].map((s) => (
            <div key={s.label} style={{ background: "#111827", borderRadius: 8, padding: "0.75rem 1rem", flex: 1 }}>
              <p style={{ fontSize: 12, color: "#64748B", margin: "0 0 2px" }}>{s.label}</p>
              <p style={{ fontSize: 20, fontWeight: 500, color: "#F0F4FF", margin: 0 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 12 }}>
        {companies.map((c) => <CompanyCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}
