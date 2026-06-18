import { useState, useEffect } from "react";
import Dashboard from "./Dashboard";
import SequenceView from "./SequenceView";

const COLORS = {
  bg: "#0A0F1E",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  high: "#378ADD",
};

export default function App() {
  const [tab, setTab] = useState("accounts");
  const [companies, setCompanies] = useState([]);
  const [sequences, setSequences] = useState([]);

  useEffect(() => {
    fetch("/personalized_companies.json").then(r => r.json()).then(setCompanies);
    fetch("/sequences.json").then(r => r.json()).then(setSequences);
  }, []);

  return (
    <div style={{ background: COLORS.bg, minHeight: "100vh", fontFamily: "Inter, sans-serif", color: COLORS.text }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem" }}>
        <div style={{ display: "flex", gap: 8, marginBottom: "1.5rem" }}>
          {[
            { id: "accounts", label: "Account prioritization" },
            { id: "sequences", label: "Email sequences" },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                padding: "8px 16px", borderRadius: 8, fontSize: 13,
                fontWeight: 500, cursor: "pointer", border: "none",
                background: tab === t.id ? COLORS.high : "#111827",
                color: tab === t.id ? "#fff" : COLORS.muted,
                transition: "all 0.2s ease",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
        {tab === "accounts" && <Dashboard companies={companies} />}
        {tab === "sequences" && <SequenceView companies={sequences} />}
      </div>
    </div>
  );
}
