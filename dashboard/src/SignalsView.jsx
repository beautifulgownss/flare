import { useState } from "react";
import { Card, Badge, ScoreMeter, Tag, Splash } from "./hockney/components";

function StatCard({ label, value }) {
  return (
    <Card padding="var(--space-4)" style={{ flex: 1 }}>
      <p className="splash-kicker" style={{ margin: "0 0 6px" }}>{label}</p>
      <p style={{ font: "var(--type-h2)", margin: 0 }}>{value}</p>
    </Card>
  );
}

const PRIORITY = {
  "High priority": { variant: "high", color: "coral" },
  "Medium priority": { variant: "medium", color: "pool" },
};

function CompanySignalCard({ company }) {
  const [expanded, setExpanded] = useState(false);
  const rec = PRIORITY[company.final_recommendation] || { variant: "low", color: "pool" };
  const isHot = (company.total_signal_score || 0) >= 9;

  return (
    <Card accent={rec.color} bar={company.final_recommendation === "High priority"}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {isHot && <Splash size={18} color="coral" strokeWidth={5} />}
          <div>
            <p style={{ font: "var(--type-h3)", margin: "0 0 2px" }}>{company.name}</p>
            <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0 }}>{company.domain}</p>
          </div>
        </div>
        <Badge variant={rec.variant}>{company.final_recommendation}</Badge>
      </div>

      <ScoreMeter label="Base score" value={company.score} color="pool" />
      <div style={{ marginTop: "var(--space-3)" }}>
        <ScoreMeter label="Signal score" value={company.total_signal_score} color="coral" />
      </div>
      <div style={{ borderTop: "var(--border-hairline) solid var(--ink)", margin: "var(--space-3) 0" }} />
      <ScoreMeter label="Composite score" value={company.composite_score} color="lawn" />

      {(company.job_reasons?.length > 0 || company.news_reasons?.length > 0) && (
        <>
          <div style={{ borderTop: "var(--border-hairline) solid var(--ink)", margin: "var(--space-3) 0" }} />
          <div
            onClick={() => setExpanded(!expanded)}
            style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
          >
            <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>
              {(company.job_reasons?.length || 0) + (company.news_reasons?.length || 0)} signals detected
            </span>
            <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>{expanded ? "−" : "+"}</span>
          </div>

          {expanded && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: "var(--space-3)" }}>
              {company.job_reasons?.map((r, i) => (
                <Tag key={`j${i}`} type="job">{r}</Tag>
              ))}
              {company.news_reasons?.map((r, i) => (
                <Tag key={`n${i}`} type="news">{r}</Tag>
              ))}
            </div>
          )}
        </>
      )}
    </Card>
  );
}

export default function SignalsView({ companies }) {
  if (!companies.length) {
    return <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "var(--space-6)" }}>Loading signals...</p>;
  }

  const high = companies.filter(c => c.final_recommendation === "High priority").length;
  const med = companies.filter(c => c.final_recommendation === "Medium priority").length;
  const avgComposite = (companies.reduce((a, c) => a + (c.composite_score || 0), 0) / companies.length).toFixed(1);

  return (
    <div>
      <div style={{ borderBottom: "var(--border-base) solid var(--ink)", paddingBottom: "var(--space-4)", marginBottom: "var(--space-5)" }}>
        <p className="splash-kicker" style={{ margin: "0 0 4px" }}>lead scoring · live signals</p>
        <h1 style={{ font: "var(--type-h1)", margin: "0 0 var(--space-4)" }}>Signal-weighted scoring</h1>
        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <StatCard label="High priority" value={high} />
          <StatCard label="Medium priority" value={med} />
          <StatCard label="Avg composite score" value={avgComposite} />
          <StatCard label="Signal sources" value="Jobs + News" />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "var(--space-3)" }}>
        {companies.map((c) => <CompanySignalCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}
