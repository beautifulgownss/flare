# Hockney — Design System

**Hockney** is the visual identity for a GTM signal-to-outreach pipeline: a tool that takes a list of company domains, enriches them with real contacts, scores each account for ICP fit, layers in live job/news signals, generates personalized outreach, and syncs everything into a CRM.

The identity is built around one idea — **a signal breaking the surface**. The signature mark is *the splash*: a flat sonar ping (a solid core broadcasting ticks) that appears wherever something surfaces (a high-priority account, a hot live signal, a successful sync). The system is deliberately **graphic and legible, not dark-mode SaaS default**: flat color fields, hard ink outlines, offset hard shadows (never blur), sharp corners, on a pale paper canvas.

> Brand line: **"Signals, surfaced."**

---

## Sources

This system was derived from a real product codebase. If you have access, explore them to build more accurate work:

- **GitHub:** https://github.com/beautifulgownss/gtm-enrichment-pipeline (`dashboard/src/` subtree — the original React dashboard; note its visuals are the *old* dark-mode direction this system replaces)
- **Local codebase explored:** `gtm-enrichment-pipeline/` — Python pipeline (`src/`), sample data (`data/`), and the React dashboard (`dashboard/src/`). The UI kit's content (accounts, openers, sequences, runs, sync status) is lifted verbatim from `data/`.

The product structure (five views: Account Prioritization, Email Sequences, Live Signals, Run History, HubSpot Sync) comes from the codebase. The **visual language is new** — defined by the brand brief, not copied from the dark-mode original.

---

## Content fundamentals

How Splash writes. Pulled from the real product copy in the codebase.

- **Voice:** confident, plain-spoken, a little contrarian. Short declaratives. It explains *why now*, not just *what*. Example product line: *"Static data tells you who a company is. Live signals tell you why now is the right time."*
- **Person:** addresses the user as **you** ("accounts worth re-engaging surface", "a CRM a sales team actually works from"). Generated outreach is first-person from the rep ("I'd love to show you…").
- **Casing:** **Sentence case** everywhere — headlines, buttons, nav. The only uppercase is the **mono kicker label** above a title and small tags (`RUN OUTPUT · ACCOUNT PRIORITIZATION`, `JOB`, `NEWS`). Never Title Case headings.
- **Numbers are the hero.** Scores (`9.7`), counts, durations (`21.4s`), costs (`$0.01`), domains, run IDs — always set in **Space Mono**. The product is quantitative; the type respects that.
- **Tone words:** "enrich", "score", "surface", "signal", "composite", "high priority", "synced". Avoid hype adjectives ("revolutionary", "seamless"). Prefer the verb the pipeline actually does.
- **No emoji.** The original codebase used a couple (✉, ✅) — Splash replaces all of them with the splash mark or Lucide icons.
- **Microcopy is direct and honest:** *"No contacts found — low discoverability. Skipped for outreach."* States the fact, says what happened, no apology.

---

## Visual foundations

**Palette.** Three flat accents on a warm pale canvas. No gradients, anywhere, ever.
- **Pool blue `#1296C7`** — primary / interactive / info; the default brand color and medium-priority bucket.
- **Coral `#FF5A3C`** — priority, hot signals, "now"; the high-priority bucket.
- **Lawn green `#3FAE2E`** — success, synced, positive deltas.
- **Canvas `#F2ECDD`** (pale paper surface) · **Paper `#FCFAF4`** (cards) · **Ink `#181512`** (outlines, text, default shadows) with soft/faint steps.
- Each accent has a **pale tint** (`--pool-blue-pale`, etc.) for tag fills and avatars — solid flat fills, never gradients.

**Type.** Three families (chosen — see *Font substitution* below):
- **Archivo** (display/headings/numeral emphasis) — black weight, tight `−0.02em` tracking. Graphic and bold.
- **Hanken Grotesk** (body/UI) — humanist, legible at 13–16px.
- **Space Mono** (data, domains, run IDs, scores, kicker labels) — characterful monospace; carries all quantitative content.

**Borders & corners.** Hard ink outlines: `1.5px` hairline / `2px` base / `3px` bold. **Corners are sharp — `border-radius: 0` everywhere.** The only exception is the rare circular avatar (`--radius-pill`).

**Shadows.** Flat, hard, **offset 4px, no blur, ever.** Default shadow is ink (`4px 4px 0 var(--ink)`). Accent shadows (`--shadow-pool/coral/lawn`) are used when a signal "breaks the surface" — e.g. a focused input, the latest run, a synced row. There are no soft/blurred shadows and no inner shadows in this system.

**Cards.** Warm paper fill, `2px` ink outline, `4px` offset shadow (ink or accent), sharp corners. High-signal cards add a `6px` **accent bar** along the top edge and lift `−2px` on hover (shadow grows to `6px`). No translucency, no backdrop blur.

**Motion.** Snappy and mechanical — `--ease-snap` (`cubic-bezier(0.2,0,0.1,1)`), `90–140ms`. No bounce, no long fades, no decorative loops. The signature interaction is **press = travel into the shadow**: buttons translate `+2px,+2px` and the shadow shrinks to `2px`, as if pressed flat against the page.

**Hover / press states.**
- *Hover:* cards lift (shadow grows, element moves up-left); nav/buttons keep fills, no color shift needed.
- *Press:* element travels into its shadow (translate + shadow shrink). No opacity dimming, no scale.
- *Focus:* a `4px` offset **accent** shadow pops in (inputs) — the surface signal.

**Imagery.** The system is **illustration-light**: the splash mark and flat color fields do the visual work. No photography, no gradients, no textures. If imagery is ever needed, it should be flat, high-contrast, and warm to sit on the canvas.

**Layout.** Pale canvas background; ink-outlined panels float on it with offset shadows. Sidebar nav (left, `2px` ink right border). Generous `24–32px` gutters. Content max ~980–1120px. Stat rows are equal-width ink-outlined cards with a big Archivo numeral over a mono label.

### Font substitution

The source product shipped **no brand fonts** (it used system UI + Inter + generic monospace). Archivo, Hanken Grotesk, and Space Mono were **chosen** to express this identity and are loaded from Google Fonts (`tokens/fonts.css`). They are not substitutes for a known brand face. **If you have official Splash fonts, drop the files in and replace the `@import` in `tokens/fonts.css` with `@font-face` rules.**

---

## Iconography

- **Primary mark:** *the splash* — a flat "sonar" ping (solid core diamond broadcasting eight ticks). Used as the logomark and as an inline signal flag. Authored as flat SVG (`assets/splash.svg`, `-pool`, `-lawn`) and as the `<Splash>` React component (color + size only; geometry never changes).
- **UI icons:** **Lucide** (https://lucide.dev), loaded from CDN in the dashboard (`target`, `mail`, `radio`, `history`, `refresh-cw`). Lucide's `2px`, sharp, geometric stroke matches the hard-outline language. Use Lucide for all functional UI icons.
- **No emoji**, no unicode glyph icons. The original codebase's emoji (✉ ✅ ▲ ▼) are replaced by Lucide icons, the splash mark, or simple `+ / —` mono affordances.
- **Substitution flag:** Lucide is a CDN substitute — the source product had no icon set of its own. Swap if a house icon library exists.

---

## What's in here (manifest)

**Root**
- `styles.css` — the single entry point consumers link (`@import` lines only).
- `tokens/` — `colors.css`, `typography.css`, `spacing.css`, `shadows.css`, `fonts.css`, `base.css`.
- `assets/` — `splash.svg`, `splash-pool.svg`, `splash-lawn.svg` (the signature mark).
- `SKILL.md` — Agent-Skills-compatible entry for using this system in Claude Code.

**Components** (`components/core/` — `window.SplashDesignSystem_d1fb1a.*`)
- `Splash` — the signature sonar mark.
- `Button` — flat, hard-outlined, press-into-shadow. primary / priority / success / secondary / ghost.
- `Badge` — status & priority chips (high / medium / low / synced / failed).
- `Tag` — pale-fill signal tags (job / news / funding / growth).
- `Card` — the core surface (accent shadow + optional top bar + hover lift).
- `ScoreMeter` — flat ink-outlined score bar.
- `Avatar` — initials in a flat tinted square.
- `Input` — text field with focus-shadow.

**UI kit** (`ui_kits/dashboard/`)
- `index.html` — interactive five-view GTM pipeline dashboard (Accounts · Sequences · Live signals · Run history · HubSpot sync), built from the real pipeline data in `data.js`.

**Specimen cards** (`guidelines/*.card.html`) — Colors, Type, Spacing, Brand foundation cards rendered in the Design System tab.

---

## Using it

Link the one stylesheet and read components off the namespace:

```html
<link rel="stylesheet" href="styles.css">
<script src="_ds_bundle.js"></script>
<script>const { Splash, Button, Card } = window.SplashDesignSystem_d1fb1a;</script>
```

Style with the CSS custom properties (`var(--coral)`, `var(--shadow-hard)`, `var(--font-display)`) — never hard-code the hexes. Keep corners sharp, shadows flat, and let the splash mark the moments where a signal surfaces.
