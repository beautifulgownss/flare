import React from "react";

const TINTS = {
  pool: { bg: "var(--pool-blue-pale)", fg: "var(--pool-blue-deep)" },
  coral: { bg: "var(--coral-pale)", fg: "var(--coral-deep)" },
  lawn: { bg: "var(--lawn-pale)", fg: "var(--lawn-deep)" },
  ink: { bg: "var(--canvas-deep)", fg: "var(--ink)" },
};

function initials(name) {
  if (!name) return "?";
  return name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
}

/**
 * Avatar — initials in a flat tinted square with a hard ink outline. Square by
 * default (sharp corners); pass `round` for the rare circular case.
 */
export function Avatar({ name, size = 36, tint = "pool", round = false, style, ...rest }) {
  const t = TINTS[tint] || TINTS.pool;
  return (
    <div
      style={{
        width: size,
        height: size,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: t.bg,
        color: t.fg,
        border: "var(--border-base) solid var(--ink)",
        borderRadius: round ? "var(--radius-pill)" : 0,
        font: `var(--weight-bold) ${Math.round(size * 0.34)}px/1 var(--font-mono)`,
        letterSpacing: "0.02em",
        ...style,
      }}
      {...rest}
    >
      {initials(name)}
    </div>
  );
}
