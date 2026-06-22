import { useState, useEffect } from "react";
import Dashboard from "./Dashboard";
import SequenceView from "./SequenceView";
import SignalsView from "./SignalsView";
import ObservabilityView from "./ObservabilityView";
import HubSpotSyncView from "./HubSpotSyncView";
import { Splash, Button } from "./hockney/components";

const TABS = [
  { id: "accounts", label: "Account prioritization" },
  { id: "sequences", label: "Email sequences" },
  { id: "signals", label: "Live signals" },
  { id: "runs", label: "Run history" },
  { id: "hubspot", label: "HubSpot sync" },
];

export default function App() {
  const [tab, setTab] = useState("accounts");
  const [companies, setCompanies] = useState([]);
  const [sequences, setSequences] = useState([]);
  const [signals, setSignals] = useState([]);
  const [runs, setRuns] = useState([]);
  const [hubspotStatus, setHubspotStatus] = useState(null);

  useEffect(() => {
    fetch("/personalized_companies.json").then(r => r.json()).then(setCompanies);
    fetch("/sequences.json").then(r => r.json()).then(setSequences);
    fetch("/companies_final.json").then(r => r.json()).then(setSignals);
    fetch("/runs_export.json").then(r => r.json()).then(setRuns);
    fetch("/hubspot_sync_status.json").then(r => r.json()).then(setHubspotStatus).catch(() => setHubspotStatus(null));
  }, []);

  return (
    <div style={{ background: "var(--surface-canvas)", minHeight: "100vh", font: "var(--type-body)", color: "var(--text-strong)" }}>
      <div style={{ maxWidth: "var(--container-max)", margin: "0 auto", padding: "var(--gutter)" }}>

        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: "var(--space-6)" }}>
          <Splash size={36} color="coral" />
          <div>
            <h1 style={{ font: "var(--type-h2)", margin: 0 }}>GTM Enrichment Pipeline</h1>
            <p className="splash-kicker" style={{ margin: "2px 0 0" }}>Signals, surfaced.</p>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, marginBottom: "var(--space-6)", flexWrap: "wrap" }}>
          {TABS.map(t => (
            <Button
              key={t.id}
              size="sm"
              variant={tab === t.id ? "primary" : "secondary"}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </Button>
          ))}
        </div>

        {tab === "accounts" && <Dashboard companies={companies} />}
        {tab === "sequences" && <SequenceView companies={sequences} />}
        {tab === "signals" && <SignalsView companies={signals} />}
        {tab === "runs" && <ObservabilityView runs={runs} />}
        {tab === "hubspot" && <HubSpotSyncView status={hubspotStatus} />}
      </div>
    </div>
  );
}
