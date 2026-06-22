import { useState } from "react";
import { Card, Badge, Avatar } from "./hockney/components";

function StatCard({ label, value }) {
  return (
    <Card padding="var(--space-4)" style={{ flex: 1 }}>
      <p className="splash-kicker" style={{ margin: "0 0 6px" }}>{label}</p>
      <p style={{ font: "var(--type-h2)", margin: 0 }}>{value}</p>
    </Card>
  );
}

const STEP_META = {
  intro: { label: "Step 1 · Intro", variant: "medium" },
  follow_up: { label: "Step 2 · Follow-up", variant: "medium" },
  breakup: { label: "Step 3 · Breakup", variant: "low" },
};

function EmailStep({ step, isActive, onClick }) {
  const meta = STEP_META[step.type] || { label: `Step ${step.step}`, variant: "neutral" };

  return (
    <div
      onClick={onClick}
      style={{
        background: isActive ? "var(--paper)" : "transparent",
        border: `var(--border-base) solid ${isActive ? "var(--ink)" : "var(--canvas-deep)"}`,
        padding: "var(--space-3)",
        cursor: "pointer",
        marginBottom: "var(--space-2)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Badge variant={meta.variant}>{meta.label}</Badge>
          <span style={{ font: "var(--type-small)", fontWeight: "var(--weight-semibold)" }}>{step.subject}</span>
        </div>
        <span style={{ font: "var(--type-small)", color: "var(--text-muted)" }}>{isActive ? "−" : "+"}</span>
      </div>

      {isActive && (
        <div style={{ background: "var(--surface-well)", border: "var(--border-hairline) solid var(--ink)", padding: "var(--space-3)", marginTop: "var(--space-3)" }}>
          <p className="splash-kicker" style={{ margin: "0 0 8px" }}>body</p>
          <pre style={{ font: "var(--type-small)", margin: 0, whiteSpace: "pre-wrap", lineHeight: "var(--leading-body)", fontFamily: "var(--font-body)" }}>
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
      <Card style={{ opacity: 0.55 }}>
        <p style={{ font: "var(--type-h3)", margin: "0 0 4px" }}>{company.name}</p>
        <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0 }}>{company.domain}</p>
        <p style={{ font: "var(--type-small)", color: "var(--text-muted)", fontStyle: "italic", marginTop: "var(--space-3)" }}>Skipped — low priority</p>
      </Card>
    );
  }

  return (
    <Card accent="pool" bar>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
        <div>
          <p style={{ font: "var(--type-h3)", margin: "0 0 2px" }}>{company.name}</p>
          <p style={{ font: "var(--type-mono)", color: "var(--text-muted)", margin: 0 }}>{company.domain}</p>
        </div>
        <Badge variant="medium">{company.sequence.length} emails</Badge>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10, background: "var(--surface-well)", border: "var(--border-hairline) solid var(--ink)", padding: "var(--space-3)", marginBottom: "var(--space-3)" }}>
        <Avatar name={company.contact} size={30} tint="pool" />
        <div>
          <p style={{ font: "var(--type-small)", fontWeight: "var(--weight-semibold)", margin: "0 0 1px" }}>{company.contact}</p>
          <p style={{ font: "var(--type-small)", color: "var(--text-muted)", margin: 0 }}>{company.title}</p>
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
    </Card>
  );
}

export default function SequenceView({ companies }) {
  if (!companies.length) {
    return <p style={{ color: "var(--text-muted)", textAlign: "center", padding: "var(--space-6)" }}>Loading sequences...</p>;
  }

  const total = companies.filter(c => c.sequence).length;

  return (
    <div>
      <div style={{ borderBottom: "var(--border-base) solid var(--ink)", paddingBottom: "var(--space-4)", marginBottom: "var(--space-5)" }}>
        <p className="splash-kicker" style={{ margin: "0 0 4px" }}>outbound sequence generator · run output</p>
        <h1 style={{ font: "var(--type-h1)", margin: "0 0 var(--space-4)" }}>Email sequences</h1>
        <div style={{ display: "flex", gap: "var(--space-3)" }}>
          <StatCard label="Sequences generated" value={total} />
          <StatCard label="Emails per sequence" value={3} />
          <StatCard label="Total emails" value={total * 3} />
          <StatCard label="Accounts skipped" value={companies.length - total} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "var(--space-3)" }}>
        {companies.map((c) => <SequenceCard key={c.domain} company={c} />)}
      </div>
    </div>
  );
}
