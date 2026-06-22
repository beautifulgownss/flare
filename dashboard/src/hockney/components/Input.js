import React from "react";

/**
 * Input — a flat text field with a hard ink outline. On focus a 4px offset
 * accent shadow appears (the signal breaking the surface). Sharp corners.
 */
export function Input({
  label,
  prefix,
  accent = "pool",
  style,
  wrapStyle,
  disabled = false,
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const shadow = { pool: "var(--pool-blue)", coral: "var(--coral)", lawn: "var(--lawn)" }[accent] || "var(--pool-blue)";
  return (
    <label style={{ display: "block", ...wrapStyle }}>
      {label && (
        <span
          style={{
            display: "block",
            font: "var(--weight-bold) 11px/1.3 var(--font-mono)",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "var(--ink-faint)",
            marginBottom: 6,
          }}
        >
          {label}
        </span>
      )}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          background: "var(--paper)",
          border: "var(--border-base) solid var(--ink)",
          borderRadius: 0,
          boxShadow: focus ? `4px 4px 0 ${shadow}` : "none",
          transition: "box-shadow var(--dur-fast,90ms) var(--ease-snap)",
          opacity: disabled ? 0.5 : 1,
        }}
      >
        {prefix && (
          <span
            style={{
              padding: "0 0 0 12px",
              font: "var(--weight-regular) 14px/1 var(--font-mono)",
              color: "var(--ink-faint)",
            }}
          >
            {prefix}
          </span>
        )}
        <input
          disabled={disabled}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            flex: 1,
            border: "none",
            outline: "none",
            background: "transparent",
            padding: "10px 12px",
            font: "var(--weight-regular) 15px/1.3 var(--font-body)",
            color: "var(--ink)",
            borderRadius: 0,
            ...style,
          }}
          {...rest}
        />
      </div>
    </label>
  );
}
