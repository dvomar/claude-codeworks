---
name: mdv-optimize-ui-ux
description: 'Improve an interface that already exists — a screen, flow, form, navigation, header or dashboard whose code you can read. Analyzes the current implementation, researches current best practices (context7 + web), produces 3 genuinely different self-contained HTML proposals each covering desktop, tablet and mobile, compares them, recommends one and implements the chosen one. Use for "optimalizuj UI/UX", "předělej design", "navrhni jak vylepšit", "vytvoř návrhy", "3 návrhy", "udělej to hezčí/přehlednější", "improve the UX of X", "redesign the login/nav/dashboard" — and also when the user only names the annoyance ("tohle je nepřehledné", "nikdo to nenajde", "zalamuje se to") without saying design. Pick by input: an existing UI to improve → this skill; code with no usable UI yet → /mdv-code-design-ui-ux; a brief with no codebase → /mdv-frontend-design.'
user-invocable: true
---

# Skill: UI/UX optimization with 3 competing proposals

Produces **decision-ready design proposals** for a piece of interface: three different strategies, each rendered for desktop / tablet / mobile as a self-contained HTML page, each honest about what it costs — followed by implementation of whichever the user picks.

The value is **not** in the HTML. It is in (a) knowing exactly how the thing works today, and (b) offering genuinely different strategies instead of three shades of the same idea. The HTML only presents that work.

## When to use

- "Optimalizuj UI a UX <čeho>" / "improve the UX of X"
- "Navrhni 3 způsoby, jak vylepšit <prvek/tok>"
- "Předělej <hlavičku / přihlašování / dashboard / formulář>"
- The user only names the pain: "je to nepřehledné", "nikdo to nenajde", "na mobilu se to rozbije", "zalamuje se to"
- A whole block: "projdi celou klientskou sekci a navrhni lepší UX"

If the user wants a *brand-new* screen with no existing implementation, this skill still fits — step 1 just becomes "map the surrounding conventions" instead of "map the current implementation".

---

## Step 1 — Map what exists (never skip)

Designing before reading the code produces proposals that can't be built or that "fix" things that already work. Find and read **every touchpoint** of the target, not just the obvious one.

For the given area, establish:

| What | Why it matters |
|---|---|
| Every component/page that renders it | The same concept is usually rendered in 2–3 places that drifted apart |
| All **states** (logged out / in, empty, loading, error, one item vs many, long names) | Most UX defects live in the states nobody designed |
| **Breakpoints** actually used (`sm/md/lg/xl`, hamburger thresholds) | Tablet is where things usually break |
| Server vs client component boundary | Decides whether a proposal is cheap or a refactor |
| Existing primitives to reuse (modal, confirm, toast, menu) | A proposal reusing them is far cheaper |
| Accessibility today (roles, labels, focus, keyboard) | You will be asked to not regress it |
| Design tokens — colors, fonts, radii, spacing | Mockups must look like *this* product |

Read the theme/`globals.css` (or equivalent) and note the real token values. Generic grey-blue Bootstrap mockups get rejected; mockups in the product's own palette get decisions.

Record defects with **evidence**: `SiteHeader.tsx:88 — "Přihlásit se" is a plain nav link among 9 others; below xl it disappears into the hamburger`. Every claim in the proposals must trace back to something you actually read.

## Step 2 — Research (both sources, briefly)

Do not design from vibes, and do not stop at generic advice either.

- **context7** — for the *implementation* pattern: the accessible spec for the widget (W3C APG `/w3c/wai-aria-practices` for menu button, dialog, disclosure, combobox…), or the framework/library docs you'll build on. This is what keeps proposals implementable and accessible.
- **web search** — for the *product* pattern: current UX guidance for this specific interaction (e.g. sign-out placement, form field order, destructive-action confirmation). Prefer sources with reasoning over listicles.

Keep it to a few targeted queries. Fold the findings into the proposals as concrete rules (keyboard map, ARIA attributes, confirmation policy), not as a bibliography.

## Step 3 — Choose three *different* strategies

This is the step that decides whether the deliverable is useful. Three variations of one idea waste the user's time — they can't make a real decision.

Force separation by giving each proposal a different **primary bet**, for example:

- **A — consolidate**: put the concern into one well-known control (menu / panel / single entry point)
- **B — surface**: give it dedicated persistent space so it can't be missed (bar, rail, always-visible summary)
- **C — remove the trip**: bring it to where the user already is (modal / inline / sheet), so no context is lost

Other axes that produce real forks: progressive disclosure vs. everything visible · one shared component vs. role-specific screens · optimizing for first-time vs. returning users · density vs. calm.

Each proposal must state, in one sentence, **what it optimizes for and what it sacrifices**. A proposal with no downside is a proposal you haven't thought about — write the honest cost in a visible callout, not in fine print.

## Step 4 — Write the three HTML proposals

Copy `templates/proposal-template.html` and fill it in. It already carries the layout, device frames and callout styles — replace the `--color` variables at the top with the product's real tokens and write the content.

Each file must contain, in this order:

1. **Title + one-paragraph lead** — what changes, in plain language
2. **Teze** callout — the bet, and the problem it attacks (reference how it works today)
3. **Desktop** frames — at minimum the two states that matter most (e.g. logged out / logged in, empty / full)
4. **Tablet** frames — show what *drops out* at this width; this is where you prove you thought about it
5. **Mobile** frames — thumb reach, sheets instead of dropdowns, keyboard behaviour
6. **The flow** it changes end to end (entry → action → feedback → where the user lands)
7. **Accessibility** — keyboard map and ARIA, taken from the context7 pattern
8. **"Co se mění oproti dnešku"** — a 3-column table: place · today (`.bad`) · proposal (`.good`)
9. **Honest cost** — a `.warn` callout with the tradeoff this specific proposal carries
10. **Cena implementace** — components touched, whether DB/API change, reuse of existing primitives, risk level

Rules that keep these useful:

- **Self-contained.** Inline CSS only, no external fonts/scripts/images — the user opens the file from disk.
- **Mockups are HTML/CSS boxes, not screenshots.** They must be readable at a glance; annotate with short notes explaining *why*, not what.
- **Use the product's real copy and real data** (actual labels, actual names/roles from the app). Lorem ipsum hides problems like long names wrapping.
- **UI language follows the product.** Czech product → Czech mockups and Czech notes.
- Write to `docs/uiux/<area>/navrh-<a|b|c>-<slug>.html` unless the user names another location.

## Step 5 — Compare, recommend, let the user choose

In chat (not only in the files): a compact comparison of the three on the axes that actually differ, then **your recommendation with reasoning**, including which one you would *not* build and why.

Then use `AskUserQuestion` so the choice is one click — options A / B / C (+ combinations if they're coherent). Offer previews in the option text so the user doesn't have to open all three files to decide.

Do not start implementing before the user picks. Producing the proposals is the deliverable of this step.

## Step 6 — Implement the chosen one

Once picked, treat it as a normal implementation task under the repo's conventions:

- Follow existing patterns and primitives found in step 1; prefer extending a shared component over forking it.
- **Do not silently drop functionality** that the mockup didn't draw. If the chosen design has no place for an existing action (edit, delete, filter), say so explicitly and either keep it behind a sensible affordance or get the user's agreement to remove it.
- Keep accessibility at least as good as before — the keyboard map from step 4 is the acceptance criterion.
- Verify at all three widths before declaring done; check the states from step 1 (long names, empty, error), not just the happy path.
- Report what you changed against the "Co se mění" table so the user can tick it off.

---

## Quality bar

The difference between a proposal that gets built and one that gets ignored:

- **Grounded** — every "dnes je to takhle" claim comes from code you read, and you can name the file.
- **Different** — the three options lead to different products, not different paddings.
- **Honest** — each option names its own cost; the recommendation names a loser.
- **Complete across widths** — tablet is not "desktop but narrower"; say what drops.
- **Buildable** — reuses what exists, states the risk, no hand-waving about "we'd add a design system".

## Common failure modes

| Failure | Fix |
|---|---|
| Three variants of one idea | Force different primary bets (step 3) |
| Generic mockups that look like Bootstrap | Read the theme tokens first, use them |
| Proposals invent a problem that doesn't exist | Step 1 with evidence; verify the complaint is real |
| Tablet section is a copy of desktop | Decide explicitly what drops at each width |
| Chosen design quietly removes a feature | Flag it before implementing (step 6) |
| Beautiful mockup that needs a rewrite to build | State the cost honestly; prefer reuse |

## Bundled resources

- `templates/proposal-template.html` — the scaffold for step 4: device frames, callouts (`.thesis`, `.warn`, `.note`), comparison table styles, mock chrome (header, menu, phone, sheet). Start from it every time; only swap the tokens and write content.
