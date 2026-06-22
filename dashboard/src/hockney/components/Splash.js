import React from "react";

const BARS = [
  { x: 12, y: 64 },
  { x: 32, y: 50 },
  { x: 52, y: 36 },
  { x: 72, y: 20 },
];
const BAR_WIDTH = 14;
const BASE_Y = 82;

const FILLS = {
  coral: "var(--coral)",
  pool: "var(--pool-blue)",
  lawn: "var(--lawn)",
  ink: "var(--ink)",
  paper: "var(--paper)",
};

export function Splash({
  size = 48,
  color = "coral",
  outline = "var(--ink)",
  ticks = true,
  strokeWidth = 3,
  spin = false,
  title,
  style,
  ...rest
}) {
  const fill = FILLS[color] || color;
  const bars = ticks ? BARS : BARS.slice(-1);

  return (
    <svg
      role={title ? "img" : "presentation"}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      viewBox="0 0 100 100"
      width={size}
      height={size}
      style={{
        display: "inline-block",
        flexShrink: 0,
        animation: spin ? "splash-pop var(--dur-base, 140ms) var(--ease-snap, ease)" : undefined,
        ...style,
      }}
      {...rest}
    >
      {bars.map((b, i) => {
        const isLast = i === bars.length - 1;
        return (
          <rect
            key={i}
            x={b.x}
            y={b.y}
            width={BAR_WIDTH}
            height={BASE_Y - b.y}
            fill={isLast ? fill : "var(--paper)"}
            stroke={outline}
            strokeWidth={strokeWidth}
            strokeLinejoin="miter"
          />
        );
      })}
    </svg>
  );
}