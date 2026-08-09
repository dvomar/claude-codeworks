---
name: code-design-ui-ux
description: Read an existing codebase, infer what the product is actually for and who uses it, then design the UI/UX for it — information architecture, screen inventory, interaction and state model, design tokens, accessibility — delivered as a written design spec plus a clickable self-contained HTML prototype. Grounds every screen in real entities, statuses, roles and error paths found in the code, and researches domain-specific interface conventions on the top design portals before committing to a layout. Use this whenever someone wants a UI or UX designed, redesigned, proposed or sanity-checked for code that already exists — a backend with no frontend, an internal tool nobody can use, a CLI that needs a GUI, an API that needs a console — including phrasings like "navrhni UI/UX", "jak by to mělo vypadat", "udělej z toho použitelnou appku", "design a frontend for this service", "what should the interface look like", "propose a UX for this module", or "this admin panel is unusable, redesign it". Prefer this over /frontend-design when the design must be derived from existing code rather than from a brief.
argument-hint: "[modul|cesta] [--depth full|spec|quick] [--platform web-desktop|web-responsive|mobile|desktop-native|kiosk-touch|tv] [--audience …] [--lang cs] [--dir …]"
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch, AskUserQuestion, Agent
---

# UI/UX Design From Code

Turn a codebase into a UI/UX proposal that someone could actually build and someone
else could actually use.

The hard part is not drawing screens. It is the inference chain
**code → domain → user jobs → priority → interface**. Skip it and you produce the
generic admin dashboard that fits any app and serves none. Every screen in the output
must trace back to something real in the repo — an entity, a status enum, a role, an
endpoint, an error type. That traceability is the whole quality mechanism: a design
grounded in the actual state space cannot be generic, because no other app has that
state space.

## When to use

- A backend/API/service exists, the UI does not — design it
- An internal tool works but nobody can use it — redesign it
- A module needs a UI proposal before implementation starts
- Someone asks "what should this look like" about existing code

Not for: building a UI from a written brief with no code behind it (use
`/frontend-design`), reviewing frontend code quality (`/code-review-feature`),
scoping and pricing the build (`/task-estimate`), or a stakeholder approval document
about an integration (`/integration-proposal`).

## Usage

```
/code-design-ui-ux [target] [--key value]
```

| Parameter | Default | Meaning |
|---|---|---|
| `target` | whole repo | Module, feature, or path to design for — e.g. `src/orders`, "the payout flow" |
| `--platform` | inferred | `web-desktop` · `web-responsive` · `mobile` · `desktop-native` · `kiosk-touch` · `tv` — drives target sizes, density, navigation, and the form the prototype takes |
| `--audience` | inferred | `internal-operators` · `end-customers` · `developers` · `mixed` |
| `--lang` | `cs` | Language of the deliverables |
| `--dir` | `docs/ui-ux/<kebab-target>` | Output directory |
| `--depth` | `full` | `full` (spec + prototype) · `spec` (markdown only) · `quick` (thesis + IA + screen inventory, no prototype) |

Scope discipline: if `target` is the whole repo and the repo is large, design the
**two or three highest-value flows properly** instead of every screen shallowly, and
say explicitly which flows you covered and which you deferred. A shallow design of
everything helps nobody.

## Phase 1 — Read the code for intent, not structure

You are not mapping the architecture (that is `/code-analyze-codebase`). You are
reconstructing the **product** from its implementation. If `.claude/knowledge/` exists,
read `architecture.md` and `backend.md` first — they save most of the structural
legwork and let you spend this phase on intent instead. Read for the things that
constrain the interface:

| Where you look | What it tells you about the UI |
|---|---|
| Entities / schema / models | The **nouns** the user thinks in. Field names are their vocabulary — reuse them verbatim in labels. Required vs nullable tells you what is genuinely mandatory. |
| Status enums, state machines | The **lifecycle the UI must make visible**. This is the richest single source: every state is something the user must be able to see, filter by, and act on. |
| Endpoints / handlers / commands | The **verbs** — the user's available actions. An action reachable from many call sites is a frequent one. |
| Roles, permissions, auth guards | Your **personas, for free**. Different permission sets are different jobs and usually different interfaces — not one interface with hidden buttons. |
| Validation rules, constraints | The **moments users fail**. Each rule is an inline-help or input-mask opportunity; a rule the user can only discover by submitting is a design bug. |
| Error types / exception classes | Each one needs a **human sentence and a recovery path**, not a code. |
| Background jobs, queues, webhooks, events | Things that happen **without the user** → the UI needs async feedback, progress, notifications, or optimistic state. |
| Config, feature flags, tenancy | Variants the design must survive. |
| Tests and fixtures | **Realistic sample data** — real names, real amounts, real edge values. Use these in the prototype instead of "Lorem ipsum" and "John Doe"; plausible data is what makes a prototype critique-able. |
| README, docs, commit history, issue titles | Stated intent and the problems people keep hitting. |
| Existing frontend, if any | What to keep. Never redesign away something that works and is familiar. |

For a large repo, fan out `Explore` agents in a single message — one per area
(domain model, API surface, auth/roles, jobs/eventing, existing FE) — then verify
anything load-bearing by reading the actual file yourself. Agent summaries are a map,
not evidence.

**Output of this phase — the product thesis.** One paragraph, written plainly:

> *Who* uses this, *to do what*, *how often*, and *what goes wrong for them when it
> goes wrong.*

Then state your confidence and what you had to guess. If the code genuinely does not
say who the user is, say so rather than inventing a persona — an honest "the code
suggests internal operators, but nothing confirms it" is more useful than a confident
fiction, and it tells the reader which parts of the design to challenge.

**Ask only what you cannot infer.** Two things routinely cannot be read out of code
and change every subsequent decision: **who the user actually is** (an operator doing
this 200× a day and a customer doing it once a year want opposite designs) and **the
platform and context of use** (desk, phone, gloved hands at a terminal). If either is
genuinely undetermined after reading, ask via `AskUserQuestion` with your best guess
first and the trade-off spelled out. Everything else — inferable or low-impact —
decide yourself and record the assumption in the spec. Blocking on questions you
could have answered from the repo wastes the user's time.

## Phase 2 — Jobs, ranked

Derive **3–7 jobs-to-be-done** from the nouns, verbs and roles. Each is a sentence in
the user's language, not the system's: *"reconcile yesterday's failed payouts before
the morning report"*, not *"CRUD on PayoutEntity"*.

Rank each job on **frequency × stakes**, because that ranking *is* the design:

- **High frequency** earns the shortest path — fewest clicks, default view, keyboard
  reachable, no confirmation. Speed is the feature.
- **High stakes** earns friction — confirmation, preview of consequences, and
  ideally **undo instead of a confirm dialog**, since reversibility protects users
  without taxing the 99% of the time they meant it.
- **Rare and low stakes** goes behind progressive disclosure. It does not deserve
  top-level navigation just because it exists.

An interface feels intuitive when the thing you do most is the thing that is easiest.
That is a scheduling decision, not a visual one — make it here, explicitly, and the
rest of the design follows.

## Phase 3 — Research the conventions of this software class

The durable canon is already bundled in `references/` — do not spend web searches
re-deriving Fitts's law. Spend them on what the canon cannot tell you: **what users
of this specific kind of software already expect.**

Jakob's Law is the reason this phase exists: people spend most of their time in
*other* products, so they arrive expecting your interface to work like the ones they
already know. Matching those conventions buys intuitiveness that no amount of clever
original design can.

Search for the **domain**, not for "UI best practices" (that returns platitudes):

- The software class: *warehouse management UI patterns*, *trading terminal layout*,
  *EHR chart navigation*, *CI/CD dashboard conventions*, *POS touch interface*
- The specific hard component: *large data table filtering patterns*, *multi-step
  approval flow*, *bulk action selection UX*
- Current reference implementations: what do the two or three best-known products in
  this space actually do, and why
- The stack's own design system, if the repo uses one — adopt it rather than
  inventing a parallel one

Sources worth trusting, roughly in order: **Nielsen Norman Group** (research-backed
usability), **Laws of UX** (principles with citations), **Material Design 3** and
**Apple Human Interface Guidelines** (component semantics, target sizes, platform
conventions), **W3C WAI / WCAG + ARIA Authoring Practices** (accessible component
behaviour), **Refactoring UI** (concrete visual tactics), **Smashing Magazine** and
**Interaction Design Foundation** (pattern deep-dives), plus the public design
systems — Shopify Polaris, Atlassian, IBM Carbon, GitHub Primer — which are unusually
good references for *dense, data-heavy internal tools*, which is what most codebases
turn out to need.

Two to five searches is normally enough. In the spec, record **only the findings that
actually changed a decision**, each with its source link. Research nobody acted on is
noise; if a search changed nothing, drop it.

If the environment has no network access, say so plainly in the deliverable and lean
on `references/` — do not silently present bundled knowledge as fresh research.

## Phase 4 — Information architecture

Choose the navigation model from the shape of the work, not from habit:

| The work looks like | Navigation model |
|---|---|
| A handful of unrelated areas | Top bar, flat |
| Many entity types, frequent switching | Persistent left sidebar, grouped by user's mental model — not by database table |
| One dominant object people live inside | Focus/canvas layout, everything else contextual |
| A strictly ordered process | Wizard with visible progress and back-navigation |
| Monitor-then-drill | Overview → list → detail, with the overview answering "is anything wrong right now" |
| Touch, gloves, kiosk, standing use | Large targets, few options per screen, no hover-dependent anything |

Then produce a **screen inventory table**: screen name · job it serves · entry points
· primary action · data shown · exit points. If a screen has no job from Phase 2, cut
it. If a job has no screen, the design is incomplete.

## Phase 5 — Interaction and state design

This is where most designs quietly fail: they specify the happy path and nothing else.
For **each key screen**, specify:

- **Purpose** — one sentence
- **Exactly one primary action**. If you cannot pick one, the screen is doing two
  jobs and should be split.
- **Data shown, and what is deliberately hidden** — recognition over recall means
  everything needed to *decide* is visible without navigating away; everything else
  is not.
- **The state matrix** — `empty` (first-run vs filtered-to-nothing, which need
  different copy), `loading` (skeleton if <1s, progress if longer, and keep the
  interface responsive under ~400ms or it stops feeling direct), `partial`, `error`
  (per error type from Phase 1, each with a recovery action), `success`,
  `no-permission`. A state you did not write is a state someone will ship as a blank
  screen.
- **Keyboard path** — how to complete the primary action without a mouse. For
  operator tools this is not accessibility garnish, it is the main input method.
- **Destructive actions** — prefer undo; use confirmation only when the action is
  genuinely irreversible, and then name the consequence in the button
  (*"Delete 47 invoices"*, not *"OK"*).
- **Copy** — real microcopy, in `--lang`, using the domain's vocabulary. Placeholder
  text is a deferred decision, not a design.

Then walk the **top-ranked job end to end** and count the interactions. State the
count in the spec. If the most common task takes more steps than a competent
alternative would, redesign now rather than defending it later.

## Phase 6 — Visual system and design language

Look for an existing system in this order and stop at the first hit:

1. **The repo's own** design tokens, component library, or brand — adopt it.
2. **`.claude/knowledge/design-language.md`** — the design language a previous run of
   this skill established and the user approved. Adopt it.
3. **Nothing yet** — derive a minimal one.

A second parallel system is a maintenance tax and an inconsistency generator, which
is why adoption beats derivation every time. When deriving: grayscale and layout
first, colour last, so hierarchy comes from spacing, size and weight rather than from
colour doing work it cannot do for colour-blind users. Constrained scales only — a
fixed spacing ramp, a fixed type ramp, a small semantic colour set, two or three
radii, two or three elevations. Read `references/design-system.md` for the concrete
scales and component specs.

### Working from an established design language

Once `design-language.md` exists, **this phase becomes adoption, not invention.** The
whole point of a design language is that the fifth module looks like the first
without anyone re-litigating button padding.

- **Adopt silently.** Do not restate the tokens in the module's spec — link to the
  design language and note only what this module uses.
- **Extend when you hit something genuinely new** — a component the language does not
  cover yet. Add it to the language, name the module that needed it, and say why the
  existing components would not do.
- **Changing an existing token is a change request, not an edit.** It affects every
  module already built. Raise it in "Otevřené otázky" with the cost of the change,
  and leave the token alone until a human decides. A silent fork here is how design
  systems die.
- **The status vocabulary is the highest-value shared part.** One mapping of
  `status enum → label + colour + icon`, used identically everywhere, is worth more
  to a user moving between modules than any amount of visual polish. Always check it
  before inventing a new status treatment.

## Phase 7 — Deliverables

Write to `--dir` (default `docs/ui-ux/<kebab-target>/`):

**1. `ui-ux-navrh.md`** — the design spec, in `--lang`:

```
# UI/UX návrh — <target>
## Produktová teze          ← Phase 1, incl. what was inferred vs confirmed
## Uživatelé a úlohy        ← Phase 2, ranked table
## Rešerše a co z ní plyne  ← Phase 3, only decision-changing findings + links
## Informační architektura  ← Phase 4, nav model + screen inventory
## Obrazovky                ← Phase 5, one block per screen incl. state matrix
## Vizuální systém          ← Phase 6, tokens + component notes
## Přístupnost              ← WCAG 2.2 AA checklist, honest pass/risk
## Napojení na kód          ← screen/action → real file:line, endpoint, entity
## Otevřené otázky          ← what only a human can decide, each with a recommendation
```

The **"Napojení na kód"** section is what separates this from a mood board: every
screen names the endpoints it calls, the entity it renders, and the statuses it must
handle, with `file:line`. It is also the honest test of the design — if a screen
cannot be wired to anything real, it was invented.

**2. `prototype.html`** (skip when `--depth quick|spec`) — one self-contained file,
inline CSS and JS, no CDN, no external fonts. It must be **clickable**: the top-ranked
job walkable end to end, real navigation between the key screens, visible hover/focus
states, and at least the empty and error states reachable via a small state switcher.
Populate it with **realistic data taken from the code's fixtures and enums**.

A prototype that can be clicked gets specific feedback ("this filter is in the wrong
place"); a static picture gets "looks nice". That difference is the entire reason to
build it. Start from `templates/prototype-template.html`.

### The prototype is HTML, but what it *means* depends on the platform

HTML is the prototype medium regardless of stack, because it is the only thing that
opens everywhere without a toolchain. What changes is whether it is **implementable
code or a communication artifact** — and saying which is not optional, because a
reviewer who thinks a WPF screen has already been built has been misled.

| `--platform` | The prototype is | Emit tokens as |
|---|---|---|
| `web-desktop`, `web-responsive` | Implementable — the CSS transfers directly | CSS custom properties (or the project's Tailwind/theme config) |
| `desktop-native` — Electron, Tauri | Implementable — same web runtime | CSS custom properties |
| `desktop-native` — WPF, Avalonia, WinForms, Qt | **A mockup for approving flow and layout.** Label it as such at the top of the file | XAML `ResourceDictionary` / Qt stylesheet, in the spec |
| `mobile` — React Native, Flutter | A mockup, rendered at a device viewport | theme object / `ThemeData`, in the spec |
| `mobile` — native iOS/Android | A mockup, rendered at a device viewport | SwiftUI/Compose theme values, in the spec |
| `kiosk-touch` | Mockup or implementable, depending on the host stack — say which | per host stack |

For every non-web target, the spec's "Vizuální systém" section carries the tokens **in
the stack's own format**, so the implementer copies rather than translates. Translation
by hand is where design systems drift.

Offer `/html-to-pdf` for a shareable PDF of the spec.

## Phase 8 — Verify before presenting

Do not report done until each of these is actually checked, not assumed:

1. **Every status** in the code's enums appears somewhere a user can see and filter by.
2. **Every error type** has a human message and a recovery path.
3. **Every role** has a coherent interface, not the same screen with buttons removed.
4. **No invented entities** — nothing in the design that has no basis in the repo.
5. **One primary action per screen.**
6. **Every screen has its empty, loading and error states** written.
7. **Top job interaction count** stated and defensible.
8. **Accessibility**: contrast 4.5:1 body / 3:1 large and UI, visible focus, targets
   ≥24×24 CSS px (44×44 for touch/kiosk), full keyboard path, labels on every input,
   never colour alone to carry meaning, motion respects `prefers-reduced-motion`.
9. **Prototype opens** — actually open it (`/run` or a browser) and click the main
   flow. A prototype that throws on load is worse than none.
10. **Design language honoured** — if `.claude/knowledge/design-language.md` existed,
    nothing was silently redefined. Extensions are listed; token *changes* are in
    open questions, not applied.
11. **Prototype's status is stated** — implementable code or approval mockup (see the
    platform table in Phase 7).

Then report: what you designed, what you deliberately left out, what you inferred
rather than confirmed, and the open questions.

## Phase 9 — Promote to the design language (only after approval)

**Do not write the design language until a human has approved the proposal.** Tokens
that nobody signed off on are not a standard, they are one run's guess — and
promoting them to canon means every later module inherits an unreviewed decision.
Keep them in the module's spec until then.

Once the user approves, write or update **`.claude/knowledge/design-language.md`**.
That path is deliberate: it sits with the repo's other shared conventions, gets
committed, and is auto-loaded as context by every later session — including
`/code-implement-feature`, so the people *building* the next module inherit it too,
not just the people designing it.

```
# Designový jazyk — <projekt>
## Platforma a hustota        ← platform, density, breakpoints, target sizes
## Tokeny                     ← in the stack's format (CSS vars / XAML / theme object)
## Stavový slovník            ← status enum → label + colour + icon, for the whole app
## Komponenty                 ← spec per component, with the states each must have
## Shell a navigace           ← nav model, breadcrumbs, page-head anatomy
## Vzory                      ← settled answers: bulk actions, filters, destructive ops
## Rozšíření                  ← changelog: module · what was added · why
```

Then say plainly what the next module inherits and what it will still have to decide.

**Running this on module two and onward.** The workflow does not change — Phases 1–5
run in full, because the *jobs* of a new module are genuinely new and the whole value
of this skill is deriving them from that module's code. Only Phase 6 collapses from
invention to adoption. Expect the second module to extend the language a little, the
third barely, and the fourth not at all. If module four is still adding components,
the language was underspecified — say so rather than quietly growing it forever.

## References

Read these when the phase needs them, not upfront:

- **`references/ux-foundations.md`** — Nielsen's heuristics, the laws of UX that
  actually change layout decisions, cognitive load, and the operational WCAG 2.2 AA
  checklist. Read during Phases 2, 5 and 8.
- **`references/design-system.md`** — token scales (type, spacing, colour, radius,
  elevation, motion), density, breakpoints, dark mode, and specs for the components
  that carry data-heavy tools: tables, forms, modals, toasts, empty states. Read
  during Phase 6.
- **`references/patterns.md`** — app archetypes mapped to IA and screen sets, the
  screen state matrix, and a guide to what to research per domain. Read during
  Phases 3 and 4.
- **`templates/prototype-template.html`** — self-contained prototype shell with
  tokens, screen router, and state switcher already wired.
- **`.claude/knowledge/design-language.md`** — not bundled; written by Phase 9 after
  the first proposal is approved, then read by Phase 6 of every later run. This is
  what makes module five look like module one.

Related: `/code-analyze-codebase` (run first on an unfamiliar repo — its
`knowledge/` output makes Phase 1 much faster) · `/frontend-design` (implement the
result with a strong visual point of view) · `/code-implement-feature` (build it —
it picks up `design-language.md` from `knowledge/` automatically) · `/html-to-pdf`
(share the spec).
