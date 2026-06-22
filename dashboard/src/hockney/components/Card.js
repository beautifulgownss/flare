import React from "react";

const ACCENTS = {
  none: { shadow: "var(--ink)", bar: null },
  ink: { shadow: "var(--ink)", bar: "var(--ink)" },
  pool: { shadow: "var(--pool-blue)", bar: "var(--pool-blue)" },
  coral: { shadow: "var(--coral)", bar: "var(--coral)" },
  lawn: { shadow: "var(--lawn)", bar: "var(--lawn)" },
};

/**
 * Card — the core surface. Warm paper fill, hard ink outline, flat offset
 * shadow (ink by default, or the accent color). Sharp corners. An optional
 * accent bar runs along the top edge.
 */
export function Card({
  accent = "none",
  bar = false,
  interactive = false,
  padding = "var(--space-5)",
  children,
  style,
  ...rest
}) {
  const a = ACCENTS[accent] || ACCENTS.none;
  const [hover, setHover] = React.useState(false);

  return (
    <div
      onMouseEnter={interactive ? () => setHover(true) : undefined}
      onMouseLeave={interactive ? () => setHover(false) : undefined}
      style={{
        position: "relative",
        background: "var(--surface-card)",
        border: "var(--border-base) solid var(--ink)",
        borderRadius: 0,
        boxShadow: hover ? `6px 6px 0 ${a.shadow}` : `4px 4px 0 ${a.shadow}`,
        transform: hover ? "translate(-2px,-2px)" : "none",
        transition: "transform var(--dur-base,140ms) var(--ease-snap), box-shadow var(--dur-base,140ms) var(--ease-snap)",
        padding,
        ...style,
      }}
      {...rest}
    >
      {bar && a.bar && (
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: 6,
            background: a.bar,
            borderBottom: "var(--border-base) solid var(--ink)",
          }}
        />
      )}
      {children}
    </div>
  );
}
