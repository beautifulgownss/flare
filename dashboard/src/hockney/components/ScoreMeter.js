import React from "react";

const COLORS = {
  pool: "var(--pool-blue)",
  coral: "var(--coral)",
  lawn: "var(--lawn)",
};

/**
 * ScoreMeter — a flat, ink-outlined track with a hard-edged accent fill and a
 * mono value. The brand's bar for account / signal / composite scores. No
 * rounded ends, no gradient.
 */
export function ScoreMeter({
  value = 0,
  max = 10,
  label,
  color = "pool",
  showValue = true,
  style,
  ...rest
}) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const fill = COLORS[color] || color;
  return (
    <div style={{ ...style }} {...rest}>
      {(label || showValue) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "baseline",
            marginBottom: 6,
          }}
        >
          {label && (
            <span style={{ font: "var(--weight-regular) 13px/1 var(--font-body)", color: "var(--ink-soft)" }}>
              {label}
            </span>
          )}
          {showValue && (
            <span style={{ font: "var(--weight-bold) 14px/1 var(--font-mono)", color: "var(--ink)" }}>
              {value}
              <span style={{ color: "var(--ink-faint)" }}>/{max}</span>
            </span>
          )}
        </div>
      )}
      <div
        style={{
          height: 14,
          background: "var(--paper)",
          border: "var(--border-base) solid var(--ink)",
          borderRadius: 0,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${pct}%`,
            background: fill,
            borderRight: pct > 0 && pct < 100 ? "var(--border-base) solid var(--ink)" : "none",
            transition: "width var(--dur-base,140ms) var(--ease-snap)",
          }}
        />
      </div>
    </div>
  );
}
