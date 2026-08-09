# Patterns — archetypes, screens, and what to research

Read during Phases 3 and 4.

**Contents**
1. [Identify the archetype from the code](#1-identify-the-archetype-from-the-code)
2. [Archetype → IA and screen set](#2-archetype--ia-and-screen-set)
3. [The screen state matrix](#3-the-screen-state-matrix)
4. [Recurring hard problems](#4-recurring-hard-problems)
5. [What to research, and where](#5-what-to-research-and-where)

---

## 1. Identify the archetype from the code

Most codebases fall into one of a few shapes. The signals are reliable:

| Signal in the code | Archetype |
|---|---|
| Many entities, CRUD endpoints, roles, an admin-ish surface | **Operational tool** |
| Time-series, metrics, aggregation queries, alert thresholds | **Monitoring / analytics** |
| A dominant entity with a rich status enum and transitions | **Workflow / pipeline** |
| Long-lived documents, versions, collaborative edits | **Editor / canvas** |
| Catalogue + cart + payment + fulfilment | **Transactional / commerce** |
| Public API, keys, quotas, webhooks, SDKs | **Developer console** |
| Search, ranking, facets, relevance tuning | **Discovery** |
| Hardware IO, kiosk, fixed viewport, no keyboard | **Self-service terminal** |
| Messages, threads, presence, read state | **Communication** |

A repo can be two of these. Design each area as its archetype rather than forcing one
layout across everything — a monitoring overview and an editor genuinely want
different shells.

---

## 2. Archetype → IA and screen set

Starting points, not prescriptions. The point is that each archetype has a *known*
shape users already expect (Jakob's Law), so deviating should be a decision, not an
accident.

**Operational tool** — sidebar by entity type, grouped by the user's mental model.
Screens: entity list (filter/sort/bulk) → entity detail (with activity history) →
create/edit form → settings → audit log. The detail screen is the centre of gravity;
lists exist to reach it. Everything the operator needs to decide should be on the
detail screen without further navigation.

**Monitoring / analytics** — overview → drill-down → raw. The overview answers exactly
one question: *is anything wrong right now.* If it takes reading to answer that, it
has failed. Screens: status overview, metric detail with time range, alert list and
history, entity-scoped view. Time range is a global persistent control, not per-chart.

**Workflow / pipeline** — the status enum *is* the information architecture. Screens:
board or queue grouped by status (with counts), item detail showing full transition
history and the actions legal *in this state*, exception queue for stuck items,
bulk-advance. Illegal actions should be absent or explained, never silently failing.

**Editor / canvas** — a focus layout: canvas dominant, tools contextual to selection,
everything else out of the way. Autosave with visible save state, version history,
and undo depth that survives navigation. Keyboard shortcuts are the primary interface
for repeat users.

**Transactional / commerce** — browse → detail → cart → checkout → confirmation →
order history. The checkout is the whole product: guest path, one decision per step,
visible progress, no surprise costs late, and full recovery from failed payment.

**Developer console** — quickstart first (working request in under five minutes),
then keys, usage/quota, logs and request inspector, webhooks with delivery attempts
and replay, docs alongside. Copy buttons everywhere; show real values, not
placeholders.

**Discovery** — persistent search, faceted filters showing result counts, obvious
active-filter chips with individual removal, result cards optimised for scanning, and
a genuinely useful zero-results state that suggests relaxations.

**Self-service terminal** — one decision per screen, huge targets, no hover, no
keyboard assumptions, an always-available cancel/back, an idle timeout with a warning,
and every error resolvable by the user standing there or clearly escalating to staff.
Attract loop when idle.

**Communication** — list of threads → thread → composer. Read/unread state must be
unambiguous, delivery/failure states explicit, and the composer must never lose a
draft.

---

## 3. The screen state matrix

Fill this for every screen in the spec. Missing states are the single most common
reason a good-looking design ships as a broken product — the states below are all
things the code can actually produce, so leaving them unwritten just defers the
decision to whoever implements it at 6pm.

| State | Must specify |
|---|---|
| **Loading — first** | Skeleton preserving final layout (not a spinner in a void); target under 400ms perceived |
| **Loading — refresh** | Keep old content visible, indicate refresh subtly; do not blank the screen |
| **Empty — first run** | What goes here, why it is useful, and the creating action in place |
| **Empty — filtered** | Which filters are active + clear them; distinct from first run |
| **Empty — good** | "Nothing needs attention" framed positively |
| **Partial** | Some data loaded, some failed — show what you have, mark what failed, offer retry for just that part |
| **Error — per type** | One entry per error type found in the code: human sentence + recovery control |
| **Offline / stale** | If the app can be used offline or shows cached data, say how stale and offer refresh |
| **No permission** | Explain what is missing and who grants it; never a blank page or a lie that it does not exist |
| **Success** | Confirmation of what changed, and the next likely action |
| **Busy / optimistic** | What the user sees between action and confirmation, and what happens on failure |

---

## 4. Recurring hard problems

Where designs usually go wrong, with the resolution that generally holds:

**Bulk actions** — Selection must survive pagination or be explicitly scoped ("all 50
on this page" vs "all 1,284 matching"). State the count in the action button. For
destructive bulk actions, show what will be affected before committing, and prefer a
reversible job with progress over an irreversible instant action.

**Long-running operations** — Never block the UI. Show progress with a real estimate
when possible, allow navigating away, and notify on completion. Make the result
findable later — a job history — because the user will close the tab.

**Optimistic updates** — Only for actions that rarely fail and are cheap to reverse.
Anything involving money, external systems, or irreversibility waits for
confirmation. A silently-reverted optimistic update destroys trust in every other
indicator in the product.

**Concurrent editing** — Detect conflicts and show both versions with a real choice.
Last-write-wins with no indication is data loss with extra steps.

**Filtering** — Active filters must be visible as removable chips outside the filter
panel, results must show a count, and filter state belongs in the URL so it can be
shared and bookmarked.

**Search vs filter** — Search is for finding a known item; filters are for narrowing
an unknown set. They are different controls and should look different.

**Permissions in the UI** — Hiding an action a role can never perform is right;
disabling an action the user could unlock is right *only with an explanation*. A
disabled control with no reason is the most common dead end in internal tools.

**Multi-tenancy** — The current tenant/account must be visible at all times and
switching must be unmistakable. Acting in the wrong tenant is a serious, quiet error.

**Money and units** — Always show currency and, where relevant, timezone. Never
render a raw minor-unit integer. Right-align, tabular figures, consistent decimals.

**Dates** — Absolute date on hover/detail, relative in lists ("2 hours ago"). State
the timezone when users span more than one.

---

## 5. What to research, and where

The canon is bundled in `ux-foundations.md` and `design-system.md`. Runtime searches
are for what those cannot know: **the conventions of this specific software class**,
because matching what users already use is the cheapest intuitiveness available
(Jakob's Law).

**Search for the domain and the hard component, not for "UI best practices".** The
latter returns platitudes that will not change a single decision.

Useful query shapes:
- `<domain> software UI patterns` — *warehouse management*, *loan origination*,
  *fleet dispatch*, *lab results*
- `<component> UX pattern` — *bulk selection across pagination*, *approval workflow
  interface*, *faceted search filters*
- `<market leader> <screen>` — how the two or three best-known products in this space
  actually lay it out, and why
- `<framework> design system` — if the repo has a stack with an official system,
  adopt its component semantics

**Sources, roughly in order of trust:**

| Source | Best for |
|---|---|
| **Nielsen Norman Group** (nngroup.com) | Research-backed usability findings, pattern studies, quantitative guidance |
| **Laws of UX** (lawsofux.com) | Principles with citations and clear applicability |
| **W3C WAI / ARIA Authoring Practices** | Accessible behaviour for any custom widget — authoritative, use it verbatim |
| **Material Design 3** (m3.material.io) | Component semantics, states, touch targets, motion |
| **Apple Human Interface Guidelines** | Platform convention, especially iOS/macOS/touch |
| **Refactoring UI** | Concrete visual tactics — hierarchy, spacing, colour |
| **Shopify Polaris · Atlassian · IBM Carbon · GitHub Primer** | Dense, data-heavy internal tools — the closest published analogue to what most codebases need |
| **Smashing Magazine · Interaction Design Foundation** | Long-form pattern deep dives, especially forms, tables, and complex inputs |
| **Baymard Institute** | E-commerce and checkout, if the archetype is transactional |

**Discipline:** two to five searches is normally enough. Record in the spec only the
findings that **changed a decision**, each with its link and a one-line note on what
it changed. Research nobody acted on is padding. And if the environment has no
network access, say so in the deliverable — do not present bundled knowledge as fresh
research.
