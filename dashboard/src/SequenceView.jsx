import { useState } from "react";

const COLORS = {
  bg: "#0A0F1E",
  card: "#111827",
  border: "#1E293B",
  text: "#F0F4FF",
  muted: "#64748B",
  high: "#378ADD",
  innerBg: "#0A0F1E",
};

const STEP_LABELS = {
  intro: { label: "Step 1 · Intro", color: "#185FA5", bg: "#0C447C" },
  follow_up: { label: "Step 2 · Follow-up", color: "#85B7EB", bg: "#0C447C" },
  breakup: { label: "Step 3 · Breakup", color: "#F59E0B", bg: "#633806" },
};

function EmailStep({ step, isActive, onClick }) {
  const meta = STEP_LABELS[step.type] || { label: `Step ${step.step}`, color: COLORS.muted, bg: COLORS.border };

  return (
    <div
      onClick={onClick}
      style={{
        background: isActive ? COLORS.card : "transparent",
        border: `0.5px solid ${isActive ? COLORS.high : COLORS.border}`,
        borderRadius: 10,
        padding: "0.875rem 1rem",
        cursor: "pointer",
        marginBottom: 8,
        transition: "all 0.2s ease",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: isActive ? 12 : 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            fontSize: 11, padding: "2px 8px", borderRadius: 4,
            background: meta.bg, color: meta.color, fontWeight: 500
          }}>
            {meta.label}
          </span>
          <span style={{ fontSize: 13, color: COLORS.text, fontWeight: 500 }}>{step.subject}</span>
        </div>
        <span style={{ fontSize: 12, color: COLORS.muted }}>{isActive ? "▲" : "▼"}</span>
      </div>

      {isActive && (
        <div style={{
          background: COLORS.innerBg,
          borderRadius: 8,
          padding: "12px 14px",
          marginTop: 8,
        }}>
          <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "0.04em" }}>body</p>
          <pre style={{
            fontSize: 13, color: COLORS.text, margin: 0,
            whiteSpace: "pre-wrap", lineHeight: 1.7,
            fontFamily: "Inter, sans-serif"
          }}>
            {step.body}
          </pre>
        </div>
      )}
    </div>
  );
}

function SequenceCard({ company }) {
  const [activeStep, setActiveStep] = useState(0);

  if (!company.sequence) {
    return (
      <div style={{
        background: COLORS.card, border: `0.5px solid ${COLORS.border}`,
        borderRadius: 12, padding: "1rem 1.25rem", opacity: 0.5
      }}>
        <p style={{ fontSize: 15, fontWeight: 500, color: COLORS.text, margin: "0 0 4px" }}>{company.name}</p>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: 0 }}>{company.domain}</p>
        <p style={{ fontSize: 13, color: COLORS.muted, fontStyle: "italic", marginTop: 12 }}>Skipped — low priority</p>
      </div>
    );
  }

  return (
    <div style={{
      background: COLORS.card,
      border: `0.5px solid ${COLORS.border}`,
      borderLeft: `3px solid ${COLORS.high}`,
      borderRadius: 12,
      padding: "1rem 1.25rem",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
        <div>
          <p style={{ fontSize: 16, fontWeight: 500, color: COLORS.text, margin: "0 0 2px" }}>{company.name}</p>
          <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: 0 }}>{company.domain}</p>
        </div>
        <span style={{
          fontSize: 11, padding: "3px 8px", borderRadius: 6,
          background: "#0C447C", color: "#85B7EB", fontWeight: 500
        }}>
          {company.sequence.length} emails
        </span>
      </div>

      <div style={{
        display: "flex", alignItems: "center", gap: 10,
        background: COLORS.innerBg, borderRadius: 8,
        padding: "10px 12px", marginBottom: 14
      }}>
        <div style={{
          width: 30, height: 30, borderRadius: "50%",
          background: "#0C447C", display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: 11, fontWeight: 500,
          color: "#85B7EB", flexShrink: 0
        }}>
          {company.contact?.split(" ").map(p => p[0]).join("").slice(0, 2).toUpperCase()}
        </div>
        <div>
          <p style={{ fontSize: 13, fontWeight: 500, color: COLORS.text, margin: "0 0 1px" }}>{company.contact}</p>
          <p style={{ fontSize: 12, color: COLORS.muted, margin: 0 }}>{company.title}</p>
        </div>
      </div>

      {company.sequence.map((step, i) => (
        <EmailStep
          key={i}
          step={step}
          isActive={activeStep === i}
          onClick={() => setActiveStep(activeStep === i ? -1 : i)}
        />
      ))}
    </div>
  );
}

export default function SequenceView({ companies }) {
  if (!companies.length) {
    return <p style={{ color: COLORS.muted, textAlign: "center", padding: "2rem" }}>Loading sequences...</p>;
  }

  const total = companies.filter(c => c.sequence).length;

  return (
    <div>
      <div style={{ borderBottom: `0.5px solid ${COLORS.border}`, paddingBottom: "1rem", marginBottom: "1.5rem" }}>
        <p style={{ fontSize: 12, fontFamily: "monospace", color: COLORS.muted, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          outbound sequence generator · run output
        </p>
        <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 1rem", color: COLORS.text }}>Email sequences</h1>
        <div style={{ display: "flex", gap: 12 }}>
          {[
            { label: "Sequences generated", value: total },
            { label: "Emails per sequence", value: 3 },
            { label: "Total emails", value: total * 3 },
            { label: "Accounts skipped", value: companies.length - total },
          ].map((s) => (
            <div key={s.label} style={{ background: "#111827", borderRadius: 8, padding: "0.75rem 1rem", flex: 1 }}>
              <p style={{ fontSize: 12, color: COLORS.muted, margin: "0 0 2px" }}>{s.label}</p>
              <p style={{ fontSize: 20, fontWeight: 500, color: COLORS.text, margin: 0 }}>{s.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 12 }}>
        {companies.map((c) => <SequenceCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}