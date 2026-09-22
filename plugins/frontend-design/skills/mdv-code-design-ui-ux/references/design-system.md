# Design System — tokens and component specs

Read during Phase 6, **only when there is nothing to adopt.** Check in this order
first: the repo's own tokens/component library/brand, then
`.claude/knowledge/design-language.md` (written by a previous approved run). If either
exists, adopt it and use this file only for the component specs in section 5. A second
parallel system is a maintenance tax and a permanent source of inconsistency.

**Contents**
1. [Method: grayscale first](#1-method-grayscale-first)
2. [Token scales](#2-token-scales)
3. [Density and breakpoints](#3-density-and-breakpoints)
4. [Dark mode](#4-dark-mode)
5. [Component specs](#5-component-specs)
6. [Emitting tokens as code](#6-emitting-tokens-as-code)

---

## 1. Method: grayscale first

Design the layout in grayscale and add colour last. It forces hierarchy to come from
**spacing, size and weight** rather than from colour — which matters because colour
cannot carry hierarchy for colour-blind users, in grayscale printouts, or on a washed
out screen in daylight. If the layout does not read in grayscale, colour is patching a
structural problem.

The other half of the method is **constrained scales**. Pick the values once, then
choose from the set rather than inventing new ones. Consistency at this level is most
of what separates professional-looking interfaces from amateur ones, and it is
mechanical rather than talent-dependent.

Sequence: layout and spacing → typography and hierarchy → grayscale contrast →
semantic colour → elevation and radius → motion.

---

## 2. Token scales

### Spacing — 4px base, 8px rhythm

```
space-0   0      space-3   12px    space-8   32px
space-1   4px    space-4   16px    space-10  40px
space-2   8px    space-5   20px    space-12  48px
                 space-6   24px    space-16  64px
```

Use 4px only for tight intra-component gaps (icon↔label). Everything structural sits
on 8px multiples. Spacing is the first thing the eye reads, so the single most
important rule is **gaps between groups exceed gaps within a group** — otherwise the
grouping reads backwards no matter how good the rest looks.

### Type scale — ~1.25 ratio, capped

```
text-xs    12px / 16px    labels, metadata, table captions
text-sm    14px / 20px    dense table body, secondary text
text-base  16px / 24px    body — the default, never smaller for prose
text-lg    18px / 28px    lead paragraphs, card titles
text-xl    20px / 28px    section headings
text-2xl   24px / 32px    page titles
text-3xl   30px / 36px    display, dashboards
```

Weights: 400 body, 500 emphasis and labels, 600 headings. Two weights are usually
enough; more than three looks unstable. Line length 45–75 characters for prose;
tables ignore this.

**Hierarchy comes from weight and colour before size.** Jumping font sizes to signal
importance produces a noisy page; a 14px 600-weight near-black label outranks 16px
400-weight gray reliably and quietly.

### Colour — semantic roles, not a palette

Define roles, not names. `--color-danger` survives a rebrand; `--red-500` does not.

```
Surface     surface, surface-raised, surface-sunken, overlay
Content     text, text-muted, text-subtle, text-inverse
Border      border, border-strong, border-focus
Brand       primary, primary-hover, primary-contrast
Semantic    success, warning, danger, info   (each: fg / bg / border)
```

Grays: one neutral ramp of ~10 steps does almost all the work. Give it a slight hue
(cool or warm) rather than pure neutral — pure `#808080` grays look dead next to any
saturated colour.

Rules that matter: text ≥4.5:1, large text and UI boundaries ≥3:1. Semantic colours
are always paired with an icon or text, never used alone. Saturated colour is the
scarcest resource on the page — spend it on the single primary action and on genuine
alerts, nothing else. A dashboard where six things are brightly coloured has no
hierarchy at all.

### Radius, elevation, motion

```
radius-sm  4px   inputs, chips, small controls
radius-md  8px   cards, buttons, panels
radius-lg  12px  modals, sheets
radius-full      pills, avatars
```

Elevation — three levels maximum. Shadows should be soft and layered (a tight dark
shadow plus a wide diffuse one), not one hard drop shadow. In dark mode elevation is
communicated by a *lighter surface*, not a stronger shadow, since shadows are nearly
invisible on dark backgrounds.

```
elev-1  resting cards       elev-2  dropdowns, popovers      elev-3  modals
```

Motion — fast and purposeful. Motion's job is to explain *where something came from*,
not to decorate.

```
duration-fast    100–150ms   hover, focus, small state changes
duration-base    200–250ms   dropdowns, accordions, tab switches
duration-slow    300–400ms   modals, page-level transitions
easing-out       cubic-bezier(0.16, 1, 0.3, 1)     entering (decelerate)
easing-in-out    cubic-bezier(0.4, 0, 0.2, 1)      moving
```

Anything over ~400ms feels slow on repeat use. Always honour `prefers-reduced-motion`
by reducing to opacity-only or none.

---

## 3. Density and breakpoints

Density is a product decision, not a style: an operator processing 400 rows a day
wants small type and tight rows; an occasional user wants breathing room. Choose from
the audience identified in Phase 1 and state the choice.

```
compact      row 32px, text-sm, space-2   power tools, dense tables
comfortable  row 40px, text-sm/base, space-3   default
spacious     row 48px+, text-base, space-4   consumer, touch, kiosk
```

Breakpoints — content-driven, but these are conventional:

```
sm 640   md 768   lg 1024   xl 1280   2xl 1536
```

For internal tools, design the **desktop case first** — that is where the work
happens — but ensure nothing breaks below 1024px. For kiosk/touch, there is one fixed
viewport: design for it exactly and skip responsive complexity entirely.

---

## 4. Dark mode

Only if genuinely needed; a bad dark mode is worse than none. If included:

- Not an inversion. Pure `#000` on pure `#fff` causes halation; use `#0d0f12`-ish
  surfaces and `#e6e8eb`-ish text.
- Desaturate and lighten brand/semantic colours — saturated colours vibrate on dark
  backgrounds.
- Elevation via lighter surfaces, not shadows.
- Re-check every contrast ratio; light-mode ratios do not transfer.
- Define all tokens on `:root`, override only the changed ones under
  `prefers-color-scheme: dark` and an explicit `[data-theme]` attribute, so both the
  system default and a manual toggle work.

---

## 5. Component specs

The components that carry data-heavy internal tools. For anything custom, follow the
**W3C ARIA Authoring Practices** for keyboard and role behaviour rather than
improvising.

### Buttons
Hierarchy: `primary` (one per screen) → `secondary` → `tertiary/ghost` →
`destructive`. States: default, hover, active, focus-visible, disabled, loading.
Minimum height 32px compact / 40px comfortable / 44px touch. Label with a verb and
its object — "Save changes", "Delete 47 invoices" — not "OK" and never "Submit". A
loading button keeps its width to avoid layout shift and blocks repeat submission.

### Inputs
Label above, always visible. Helper text below, error text replacing it in the same
slot so nothing jumps. Focus ring 2px, offset 2px, ≥3:1 against the adjacent colour.
Error state uses border colour **plus** an icon **plus** text. Never rely on the
placeholder to say what a field is.

### Tables — the workhorse of internal tools
- Sticky header; sticky first column when horizontally scrollable.
- Right-align numbers, use tabular figures (`font-variant-numeric: tabular-nums`) so
  digits line up; left-align text; never centre either.
- Row height fixed by density; truncate with tooltip rather than wrapping, unless the
  column is genuinely prose.
- Sort, filter and column visibility are controls above the table, not hidden in
  headers alone.
- Selection: checkbox column, a header select-all scoped to the *visible page*, and a
  bulk action bar that appears on selection stating the count explicitly.
- Pagination for exact counts, infinite scroll only for browsing (never for tasks
  needing "did I do all of them").
- Empty, loading (skeleton rows preserving layout), error, and
  filtered-to-no-results — the last is a **different state** with a "clear filters"
  action, and conflating it with genuine emptiness is a routine bug.
- Row click behaviour must be one thing consistently: either open detail or select.
  Do not mix.

### Modals and dialogs
Only for a focused decision that must block. Anything longer belongs on a page or in
a side panel. Focus moves in on open, is trapped inside, returns to the trigger on
close. Escape closes; a backdrop click closes only when there is no unsaved input.
Title states the decision; buttons state the actions ("Discard changes" / "Keep
editing"), never "Yes"/"No".

### Side panels / drawers
Better than modals when the user needs the underlying context — detail views,
filters, comments. Non-blocking, resizable when they contain a lot.

### Toasts and inline feedback
Toasts for transient success and for anything that carries an undo. Never for errors
requiring action — those go inline, next to the cause, where they persist. Auto-dismiss
after 4–6s, but never auto-dismiss anything containing the only path to undo.

### Empty states
The highest-leverage screen nobody designs. Three distinct kinds, three distinct
treatments:
- **First run** — explain what will be here, and put the primary creating action in
  the middle of the empty area.
- **Filtered to nothing** — say which filters are active, offer "clear filters".
- **Nothing to do** — the good kind ("no failed payouts"). Say so positively rather
  than showing a sad box.

### Navigation
Current location always visible. Breadcrumbs when hierarchy exceeds two levels. Group
sidebar items by the user's mental model, not by database table. Keep groups short —
Hick's Law applies hardest here, since this is the menu people read on every visit.

### Status indicators
Every status enum from the code gets a consistent visual: colour + icon + text label,
using the domain's own word. Define the mapping once in the spec and use it
everywhere — the same status must never appear as a chip in one place and coloured
text in another.

---

## 6. Emitting tokens as code

Put the tokens in the spec **and** in the prototype as CSS custom properties, so the
implementer copies rather than re-derives them:

```css
:root {
  --space-2: 8px;  --space-4: 16px;  --space-6: 24px;
  --text-sm: 14px; --text-base: 16px; --text-2xl: 24px;
  --radius-md: 8px;
  --color-surface: #ffffff;
  --color-text: #14171a;
  --color-text-muted: #5b6570;
  --color-border: #dfe3e8;
  --color-primary: #1a56db;
  --color-danger: #c0342b;
  --elev-1: 0 1px 2px rgb(16 24 40 / .06), 0 1px 3px rgb(16 24 40 / .10);
  --duration-base: 200ms;
  --easing-out: cubic-bezier(0.16, 1, 0.3, 1);
}
```

If the project uses Tailwind, express the scales as a theme config extract. If it uses
a component library, express them as that library's theme object. Matching the
project's existing mechanism is worth more than any particular value.
