const COLORS = {
  high: "#378ADD",
  low: "#888780",
  bg: "#0A0F1E",
  card: "#111827",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  green: "#22C55E",
  red: "#EF4444",
};

function StatusBadge({ status }) {
  const isSuccess = status === "success";
  return (
    <span style={{
      fontSize: 11, padding: "3px 8px", borderRadius: 6, fontWeight: 500,
      background: isSuccess ? "#0F2E1C" : "#2E1313",
      color: isSuccess ? COLORS.green : COLORS.red,
    }}>
      {isSuccess ? "Synced" : "Failed"}
    </span>
  );
}

function SyncRow({ account }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      background: COLORS.card, border: `0.5px solid ${COLORS.border}`,
      borderRadius: 10, padding: "0.85rem 1.1rem", marginBottom: 8,
    }}>
      <div>
        <p style={{ fontSize: 14, fontWeight: 500, color: COLORS.text, margin: "0 0 2px" }}>{account.name}</p>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: 0 }}>{account.domain}</p>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span style={{ fontSize: 12, color: COLORS.muted, textTransform: "capitalize" }}>{account.action}</span>
        <span style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted }}>{account.duration_ms}ms</span>
        <StatusBadge status={account.status} />
      </div>
      {account.error && (
        <p style={{ fontSize: 11, color: COLORS.red, margin: "4px 0 0", fontFamily: "monospace" }}>{account.error}</p>
      )}
    </div>
  );
}

export default function HubSpotSyncView({ status }) {
  if (!status || !status.accounts) {
    return <p style={{ color: COLORS.muted, fontSize: 13 }}>No sync data yet — run the pipeline to populate this view.</p>;
  }

  const lastSynced = status.last_synced
    ? new Date(status.last_synced).toLocaleString()
    : "—";

  return (
    <div>
      <div style={{ borderBottom: `0.5px solid ${COLORS.border}`, paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          HubSpot CRM · sync status
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 1rem" }}>HubSpot sync</h1>
        <div style={{ display: "flex", gap: 12 }}>
          {[
            { label: "Last synced", value: lastSynced },
            { label: "Total accounts", value: status.total },
            { label: "Succeeded", value: status.succeeded },
            { label: "Failed", value: status.failed },
          ].map((s) => (
            <div key={s.label} style={{ background: COLORS.card, borderRadius: 8, padding: "0.75rem 1rem", flex: 1 }}>
              <p style={{ fontSize: 12, color: COLORS.muted, margin: "0 0 2px" }}>{s.label}</p>
              <p style={{ fontSize: s.label === "Last synced" ? 13 : 20, fontWeight: 500, color: COLORS.text, margin: 0 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>
      <div>
        {status.accounts.map((a) => <SyncRow key={a.domain} account={a} />)}
      </div>
    </div>
  );
}
