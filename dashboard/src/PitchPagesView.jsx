import { Card, Badge, Splash } from "./hockney/components";

function StatCard({ label, value }) {
  return (
    <Card padding="var(--space-4)" style={{ flex: 1 }}>
      <p className="splash-kicker" style={{ margin: "0 0 6px" }}>{label}</p>
      <p style={{ font: label === "Last generated" ? "var(--type-h3)" : "var(--type-h2)", margin: 0 }}>{value}</p>
    </Card>
  );
}

function PitchPageRow({ account }) {
  const isSuccess = account.status === "success";
  return (
    <Card accent={isSuccess ? "lawn" : "coral"} style={{ marginBottom: "var(--space-2)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {isSuccess && <Splash size={16} color="lawn" strokeWidth={5} />}
          <div>
            <p style={{ font: "var(--type-small)", fontWeight: "var(--weight-semibold)", margin: "0 0 2px" }}>{account.name}</p>
            <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0, fontSize: 11 }}>{account.domain}</p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{ font: "var(--type-small)", color: "var(--text-muted)", textTransform: "capitalize" }}>{account.action}</span>
          <span style={{ font: "var(--type-mono)", color: "var(--text-muted)", fontSize: 11 }}>{account.duration_ms}ms</span>
          {isSuccess && account.company_slug && (
            <a
              href={`/pages/${account.company_slug}.html`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ font: "var(--type-small)", color: "var(--pool-blue)", textDecoration: "underline" }}
            >
              View page
            </a>
          )}
          <Badge variant={isSuccess ? "synced" : "failed"} splash={isSuccess}>{isSuccess ? "Generated" : "Failed"}</Badge>
        </div>
      </div>
      {account.error && (
        <p style={{ font: "var(--type-mono)", color: "var(--coral-deep)", margin: "var(--space-2) 0 0", fontSize: 11 }}>{account.error}</p>
      )}
    </Card>
  );
}

export default function PitchPagesView({ status }) {
  if (!status || !status.accounts) {
    return <p style={{ color: "var(--text-muted)", font: "var(--type-small)" }}>No pitch page data yet — run the pipeline to populate this view.</p>;
  }

  const lastGenerated = status.last_generated
    ? new Date(status.last_generated).toLocaleString()
    : "—";

  return (
    <div>
      <div style={{ borderBottom: "var(--border-base) solid var(--ink)", paddingBottom: "var(--space-4)", marginBottom: "var(--space-5)" }}>
        <p className="splash-kicker" style={{ margin: "0 0 4px" }}>Personalized pitch pages · generation status</p>
        <h1 style={{ font: "var(--type-h1)", margin: "0 0 var(--space-4)" }}>Pitch pages</h1>
        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <StatCard label="Last generated" value={lastGenerated} />
          <StatCard label="Total accounts" value={status.total} />
          <StatCard label="Succeeded" value={status.succeeded} />
          <StatCard label="Failed" value={status.failed} />
        </div>
      </div>
      <div>
        {status.accounts.map((a) => <PitchPageRow key={a.domain} account={a} />)}
      </div>
    </div>
  );
}
