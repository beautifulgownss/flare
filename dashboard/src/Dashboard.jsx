import { Card, Badge, ScoreMeter, Avatar, Splash } from "./hockney/components";

function StatCard({ label, value }) {
  return (
    <Card padding="var(--space-4)" style={{ flex: 1 }}>
      <p className="splash-kicker" style={{ margin: "0 0 6px" }}>{label}</p>
      <p style={{ font: "var(--type-h2)", margin: 0 }}>{value}</p>
    </Card>
  );
}

function CompanyCard({ company }) {
  const isHigh = company.recommendation === "High priority";

  return (
    <Card accent={isHigh ? "coral" : "none"} bar={isHigh} interactive style={{ opacity: isHigh ? 1 : 0.65 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {isHigh && <Splash size={18} color="coral" strokeWidth={5} />}
          <div>
            <p style={{ font: "var(--type-h3)", margin: "0 0 2px" }}>{company.name}</p>
            <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0 }}>{company.domain}</p>
          </div>
        </div>
        <Badge variant={isHigh ? "high" : "low"}>{company.recommendation}</Badge>
      </div>

      <ScoreMeter value={company.score} color={isHigh ? "coral" : "pool"} />

      <p style={{ font: "var(--type-small)", color: "var(--text-muted)", margin: "var(--space-3) 0" }}>
        {company.emails_found ?? "—"} emails found
      </p>

      {isHigh && company.best_contact_name ? (
        <>
          <div style={{ borderTop: "var(--border-hairline) solid var(--ink)", margin: "var(--space-3) 0" }} />
          <div style={{ display: "flex", gap: 10, marginBottom: "var(--space-3)" }}>
            <Avatar name={company.best_contact_name} size={32} tint="coral" />
            <div>
              <p style={{ font: "var(--type-small)", fontWeight: "var(--weight-semibold)", margin: "0 0 1px" }}>{company.best_contact_name}</p>
              <p style={{ font: "var(--type-small)", color: "var(--text-muted)", margin: "0 0 1px" }}>{company.best_contact_title}</p>
              <p style={{ font: "var(--type-mono)", color: "var(--pool-blue)", margin: 0 }}>{company.best_contact_email}</p>
            </div>
          </div>
          <div style={{ background: "var(--surface-well)", border: "var(--border-hairline) solid var(--ink)", padding: "var(--space-3)" }}>
            <p className="splash-kicker" style={{ margin: "0 0 4px" }}>opener</p>
            <p style={{ font: "var(--type-small)", margin: 0, lineHeight: "var(--leading-body)" }}>{company.opener}</p>
          </div>
        </>
      ) : (
        <p style={{ font: "var(--type-small)", color: "var(--text-muted)", fontStyle: "italic", textAlign: "center", padding: "var(--space-4) 0" }}>
          No contacts found — low discoverability
        </p>
      )}
    </Card>
  );
}

export default function Dashboard({ companies = [] }) {
  const high = companies.filter((c) => c.recommendation === "High priority").length;
  const avgScore = companies.length
    ? (companies.reduce((a, c) => a + c.score, 0) / companies.length).toFixed(1)
    : 0;

  return (
    <div>
      <div style={{ borderBottom: "var(--border-base) solid var(--ink)", paddingBottom: "var(--space-4)", marginBottom: "var(--space-5)" }}>
        <p className="splash-kicker" style={{ margin: "0 0 4px" }}>GTM enrichment pipeline · run output</p>
        <h1 style={{ font: "var(--type-h1)", margin: "0 0 var(--space-4)" }}>Account prioritization</h1>
        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <StatCard label="Companies enriched" value={companies.length} />
          <StatCard label="High priority" value={high} />
          <StatCard label="Openers generated" value={high} />
          <StatCard label="Avg score" value={avgScore} />
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "var(--space-3)" }}>
        {companies.map((c) => <CompanyCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}
