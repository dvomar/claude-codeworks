# UX Foundations

The durable canon. Bundled so runtime research can be spent on domain-specific
conventions instead of re-deriving principles that have been stable for decades.

**Contents**
1. [Nielsen's 10 usability heuristics](#1-nielsens-10-usability-heuristics)
2. [Laws that change layout decisions](#2-laws-that-change-layout-decisions)
3. [Gestalt — grouping without borders](#3-gestalt--grouping-without-borders)
4. [Cognitive load](#4-cognitive-load)
5. [Error prevention and recovery](#5-error-prevention-and-recovery)
6. [Forms](#6-forms)
7. [WCAG 2.2 AA — operational checklist](#7-wcag-22-aa--operational-checklist)
8. [How to apply this to a design](#8-how-to-apply-this-to-a-design)

---

## 1. Nielsen's 10 usability heuristics

Published by Jakob Nielsen in 1994, refined in 2020, still the standard evaluation
checklist. They are rules of thumb for spotting where users get lost, frustrated or
surprised — not layout rules.

| # | Heuristic | What it demands of your design |
|---|---|---|
| 1 | **Visibility of system status** | The user always knows what is happening. Every async action gets feedback within ~400ms. Every entity's state is visible without asking. |
| 2 | **Match between system and the real world** | Speak the user's language, not the database's. `PaymentIntent.status = requires_capture` becomes "Waiting for approval". |
| 3 | **User control and freedom** | An obvious exit from every state. Undo and redo. Never trap someone in a flow they entered by accident. |
| 4 | **Consistency and standards** | Same thing, same word, same place, same behaviour — internally, and against platform convention. |
| 5 | **Error prevention** | Better than good error messages. Constrain inputs, disable impossible actions with an explanation, confirm only destructive ones. |
| 6 | **Recognition rather than recall** | Everything needed to make a decision is visible. Do not make people remember an ID from the previous screen. |
| 7 | **Flexibility and efficiency of use** | Accelerators for experts — keyboard, bulk actions, saved filters — that novices can ignore. |
| 8 | **Aesthetic and minimalist design** | Every element competes for attention with the important ones. Rarely-used content is not merely clutter, it actively costs you. |
| 9 | **Help users recognise, diagnose and recover from errors** | Plain language, what went wrong, and a button that fixes it. No error codes as the primary message. |
| 10 | **Help and documentation** | Ideally unnecessary; when needed, in context and task-focused, not a manual elsewhere. |

Use these in Phase 8 as an evaluation pass: walk the top job and name which heuristic
each friction point violates. Naming the heuristic makes the critique actionable
instead of a matter of taste.

---

## 2. Laws that change layout decisions

Only the ones with real design consequences. Each with the *so what*.

**Jakob's Law** — Users spend most of their time on other products, so they expect
yours to work the same way. *So what:* research the two or three market-leading
products in the domain and match their conventions unless you have a specific reason
not to. This is the cheapest intuitiveness you will ever buy. Novelty in navigation
and core interaction is almost always a cost, not a feature.

**Fitts's Law** — Time to hit a target grows with distance and shrinks with size.
*So what:* the primary action is big and near where the eye already is. Frequent
actions do not live in far corners. Screen edges and corners are effectively infinite
in size (the pointer stops there) — good for persistent nav, bad for destructive
buttons. Touch targets ≥44px; a 24px target is a WCAG minimum, not a comfortable size.

**Hick's Law** — Decision time grows with the number and complexity of choices.
*So what:* fewer top-level options, progressive disclosure, sensible defaults. A menu
of 20 items is not a feature list, it is a tax paid on every visit. Break long forms
into steps; group choices into categories.

**Miller's Law** — Working memory holds roughly 5–9 chunks. *So what:* chunk long
numbers, group form fields, keep navigation groups short. Do not require carrying
information across screens.

**Doherty Threshold** — Productivity rises sharply when system response is under
~400ms. *So what:* respond to input immediately even when work is not done —
optimistic UI, skeletons, instant local validation. Perceived speed beats actual speed
for satisfaction, but never fake completion of something that can fail.

**Tesler's Law (conservation of complexity)** — Every system has irreducible
complexity; the only question is who absorbs it. *So what:* the design's job is to
move complexity from the user into the system — smart defaults, inference, automation
— not to hide it behind a clean surface where it ambushes people later.

**Postel's Law** — Be liberal in what you accept from users, conservative in what you
produce. *So what:* accept the phone number with spaces, the date in any sane format,
the pasted value with trailing whitespace. Normalise silently. Rejecting input a
machine could obviously parse is hostility, not validation.

**Aesthetic–Usability Effect** — People perceive attractive designs as more usable and
are more tolerant of minor problems. *So what:* visual polish is functional, and it
also masks usability problems in testing — do not let a pretty prototype substitute
for walking the actual task.

**Peak–End Rule** — An experience is judged by its most intense moment and its end.
*So what:* invest in the hardest moment (the difficult decision, the failure) and in
the completion moment. A good confirmation screen is disproportionately valuable.

**Serial Position Effect** — First and last items in a list are best remembered.
*So what:* put the most important navigation items at the beginning and end.

**Von Restorff (isolation) Effect** — The item that differs is remembered.
*So what:* exactly one visually dominant action per screen. Two "primary" buttons
means zero. Never rely on colour alone to do the isolating.

**Zeigarnik Effect** — Unfinished tasks stay in memory. *So what:* progress
indicators and visible incompleteness drive completion — but only where completion is
genuinely desirable, not as a dark pattern.

**Goal-Gradient Effect** — Effort increases as the goal appears closer. *So what:*
show progress, and show artificial early progress honestly (step 1 of 4 already
complete because it was inferred).

---

## 3. Gestalt — grouping without borders

Most "cluttered" interfaces are not too dense; they are grouped wrong. Reach for these
before reaching for more borders and boxes.

- **Proximity** — things near each other are read as related. The strongest and
  cheapest grouping tool. Space *between* groups must exceed space *within* a group,
  otherwise the grouping reads backwards. This single rule fixes more layouts than
  any other.
- **Common region** — a shared background or container groups items even when far
  apart. Use when proximity is not available.
- **Similarity** — same colour/shape/size reads as same kind. Do not style two
  different kinds of thing identically.
- **Closure / continuity** — the eye completes shapes and follows lines. Alignment
  along a shared edge creates order without drawing anything.
- **Figure/ground** — elevation, blur and contrast decide what is on top. Modals and
  popovers depend on this being unambiguous.

---

## 4. Cognitive load

Three kinds, and only one is worth spending:

- **Intrinsic** — inherent to the task. Irreducible; support it with good information
  design.
- **Extraneous** — caused by the interface: inconsistent labels, hidden state,
  needless steps, ambiguous icons. **This is what you are cutting.**
- **Germane** — effort spent building a useful mental model. Worth it; a consistent,
  learnable structure converts effort into fluency.

Practical reducers: consistent vocabulary drawn from the domain; defaults that are
right most of the time; the system remembering rather than asking again; showing
consequences before commitment; one decision per moment.

Icons without labels are a recall test. Use text labels for anything not universally
understood (the universal set is roughly: search, close, menu, back, settings, and
even those benefit from labels in low-frequency tools).

---

## 5. Error prevention and recovery

Ordered by preference:

1. **Make the error impossible** — constrain the input. A date picker cannot produce
   the 31st of February.
2. **Make it obvious before submitting** — validate on blur with a clear rule stated
   *before* the user types, not after they fail.
3. **Make it recoverable** — undo, drafts, autosave, non-destructive defaults.
4. **Make it understandable** — plain sentence, cause, and a button that resolves it.

Error message anatomy: **what happened** (plainly) → **why** (if actionable) →
**what to do now** (a control, not a suggestion). Never surface a stack trace or an
enum as the primary message; keep a correlation ID available for support, secondary.

Disabled controls are a common trap: a button that is disabled without saying why is
a dead end. Either explain the condition on hover/focus and adjacent text, or allow
the click and explain on attempt.

---

## 6. Forms

Forms are where most internal tools are actually used, and where they most often fail.

- One column. Multi-column forms cause skipped fields and ambiguous reading order.
- Labels above fields, always visible. Placeholder-as-label disappears exactly when
  it is needed and fails accessibility.
- Group related fields with spacing; sequence in the order the user has the
  information, not the order the database stores it.
- Mark **optional** fields rather than required ones when most are required.
- Field width signals expected length — a postcode field should not be 600px wide.
- Validate on blur, re-validate on submit, never on every keystroke while typing
  (except for genuinely live constraints like password strength or availability).
- Keep the submit button enabled and explain the failure on click; a permanently
  disabled submit with no explanation is the most common form dead end.
- Never clear entered data on error.
- State the rule up front ("at least 12 characters"), do not reveal it by rejection.
- Autofocus the first field in single-purpose forms; support paste everywhere,
  including in split OTP inputs.

---

## 7. WCAG 2.2 AA — operational checklist

Not the standard verbatim; the parts that actually decide a design. WCAG 2.2 became a
W3C Recommendation in October 2023, adding nine criteria aimed at low vision,
cognitive, and motor impairments including touch use.

**Perceivable**
- Text contrast ≥ **4.5:1**; large text (≥24px, or ≥19px bold) ≥ **3:1**.
- Non-text contrast ≥ **3:1** for UI component boundaries, icons and graphs that
  carry meaning (1.4.11).
- **Never colour alone** to convey status — pair with icon, text or shape. Roughly 1
  in 12 men cannot rely on red/green.
- Text resizes to 200% without loss of content; reflows at 320px width without
  horizontal scrolling (1.4.10).
- Every meaningful image has an alt text; decorative ones are hidden from assistive
  tech.

**Operable**
- Everything reachable and operable by keyboard, with no traps (2.1.1, 2.1.2).
- **Focus visible** (2.4.7) and **not obscured** by sticky headers, footers or
  overlays (2.4.11, new in 2.2). Sticky elements are the usual culprit — check with
  keyboard tabbing, not by eye.
- **Target size ≥ 24×24 CSS px** (2.5.8, new in 2.2), with an exception when targets
  are sufficiently spaced. For touch and kiosk aim for **44×44** — the 24px floor is a
  minimum, not a target.
- **Dragging movements** have a single-pointer alternative (2.5.7, new in 2.2) — any
  drag-to-reorder or drag-to-assign needs a menu or button path too.
- Logical focus order matching visual order; skip link to main content.
- No content that flashes more than three times per second.
- Motion respects `prefers-reduced-motion`.

**Understandable**
- **Consistent help** placement across pages (3.2.6, new in 2.2).
- **Redundant entry** avoided — do not ask for information already given in the same
  process (3.3.7, new in 2.2). Auto-populate or offer to reuse.
- **Accessible authentication** — no cognitive function test (puzzle, memorised
  password recall) without an alternative; allow paste into password and OTP fields
  (3.3.8, new in 2.2).
- Labels and instructions on every input; errors identified in text and programmatically.
- Language of the page declared.

**Robust**
- Native semantic HTML first; ARIA only to fill genuine gaps. A `<button>` beats
  `<div role="button">` every time — it brings keyboard, focus and semantics free.
- Follow the **ARIA Authoring Practices** for any custom widget (combobox, tabs,
  tree, dialog) rather than improvising roles.
- Status changes announced via live regions; focus managed on dialog open and close,
  and returned to the trigger on close.

Full detail: `w3.org/WAI/WCAG22/quickref/` and `w3.org/WAI/ARIA/apg/`.

---

## 8. How to apply this to a design

During design (Phase 2 and 5): use section 2 to make the frequency/stakes trade-offs
concrete, and section 6 whenever a screen contains a form.

During verification (Phase 8): walk the top-ranked job end to end and, at each point
of friction, name the heuristic (section 1) or law (section 2) it violates. Then run
section 7 as a checklist and report honestly — "keyboard path unverified for the bulk
action" is a useful finding; a blanket "WCAG AA compliant" that nobody checked is
worse than saying nothing.
