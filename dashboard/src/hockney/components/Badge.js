import React from "react";
import { Splash } from "./Splash";

const VARIANTS = {
  high: { bg: "var(--coral)", fg: "var(--white)", splash: "coral" },
  medium: { bg: "var(--pool-blue)", fg: "var(--white)", splash: "pool" },
  low: { bg: "var(--canvas-deep)", fg: "var(--ink-soft)", splash: null },
  synced: { bg: "var(--lawn)", fg: "var(--white)", splash: "lawn" },
  failed: { bg: "var(--ink)", fg: "var(--coral)", splash: null },
  neutral: { bg: "var(--paper)", fg: "var(--ink)", splash: null },
};

/**
 * Badge — a flat, ink-outlined status chip. Sharp corners. Optionally leads
 * with a tiny Splash when the state is a "signal" (high priority, synced).
 */
export function Badge({ variant = "neutral", splash = false, children, style, ...rest }) {
  const v = VARIANTS[variant] || VARIANTS.neutral;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        padding: "3px 9px",
        background: v.bg,
        color: v.fg,
        border: "var(--border-base) solid var(--ink)",
        borderRadius: 0,
        font: "var(--weight-bold) 11px/1.3 var(--font-mono)",
        textTransform: "uppercase",
        letterSpacing: "0.06em",
        whiteSpace: "nowrap",
        ...style,
      }}
      {...rest}
    >
      {splash && v.splash && <Splash size={14} color={v.splash} strokeWidth={6} />}
      {children}
    </span>
  );
}
