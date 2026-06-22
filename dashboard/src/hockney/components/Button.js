import React from "react";

const FILL = {
  primary: { bg: "var(--pool-blue)", fg: "var(--white)", shadow: "var(--ink)" },
  priority: { bg: "var(--coral)", fg: "var(--white)", shadow: "var(--ink)" },
  success: { bg: "var(--lawn)", fg: "var(--white)", shadow: "var(--ink)" },
  secondary: { bg: "var(--paper)", fg: "var(--ink)", shadow: "var(--ink)" },
};

const SIZES = {
  sm: { pad: "6px 12px", font: "13px", gap: 6 },
  md: { pad: "10px 18px", font: "15px", gap: 8 },
  lg: { pad: "14px 26px", font: "17px", gap: 10 },
};

/**
 * Button — flat fill, hard ink outline, 4px offset shadow. On press the button
 * travels into its own shadow. No rounded corners, no blur.
 */
export function Button({
  variant = "primary",
  size = "md",
  ghost = false,
  disabled = false,
  type = "button",
  children,
  style,
  ...rest
}) {
  const [pressed, setPressed] = React.useState(false);
  const v = FILL[variant] || FILL.primary;
  const s = SIZES[size] || SIZES.md;

  const base = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: s.gap,
    padding: s.pad,
    font: `var(--weight-bold) ${s.font}/1 var(--font-display)`,
    letterSpacing: "-0.01em",
    color: ghost ? "var(--ink)" : v.fg,
    background: ghost ? "transparent" : v.bg,
    border: "var(--border-base) solid var(--ink)",
    borderRadius: 0,
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.45 : 1,
    boxShadow: ghost ? "none" : pressed ? "2px 2px 0 var(--ink)" : "4px 4px 0 var(--ink)",
    transform: ghost ? "none" : pressed ? "translate(2px,2px)" : "none",
    transition: "transform var(--dur-fast,90ms) var(--ease-snap), box-shadow var(--dur-fast,90ms) var(--ease-snap), background var(--dur-fast,90ms)",
    userSelect: "none",
    ...style,
  };

  const handlers = disabled
    ? {}
    : {
        onMouseDown: () => setPressed(true),
        onMouseUp: () => setPressed(false),
        onMouseLeave: () => setPressed(false),
      };

  return (
    <button type={type} disabled={disabled} style={base} {...handlers} {...rest}>
      {children}
    </button>
  );
}
