import React from "react";

const TYPES = {
  job: { bg: "var(--pool-blue-pale)", label: "JOB" },
  news: { bg: "var(--coral-pale)", label: "NEWS" },
  funding: { bg: "var(--lawn-pale)", label: "FUNDING" },
  growth: { bg: "var(--canvas-deep)", label: "GROWTH" },
};

/**
 * Tag — a signal tag. Pale flat fill, hard ink outline, mono type. Leads with a
 * small uppercase type label (JOB / NEWS / FUNDING) when `type` is set.
 */
export function Tag({ type, label, children, style, ...rest }) {
  const t = TYPES[type];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "baseline",
        gap: 7,
        padding: "5px 10px",
        background: t ? t.bg : "var(--paper)",
        color: "var(--ink)",
        border: "var(--border-hairline) solid var(--ink)",
        borderRadius: 0,
        font: "var(--weight-regular) 13px/1.45 var(--font-body)",
        ...style,
      }}
      {...rest}
    >
      {(t || label) && (
        <span
          style={{
            font: "var(--weight-bold) 10px/1 var(--font-mono)",
            letterSpacing: "0.08em",
            color: "var(--ink)",
            opacity: 0.65,
            flexShrink: 0,
          }}
        >
          {label || t.label}
        </span>
      )}
      <span>{children}</span>
    </span>
  );
}
