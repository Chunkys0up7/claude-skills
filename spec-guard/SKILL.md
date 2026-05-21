---
name: spec-guard
description: |
  Enforces spec-driven discipline for projects that have specs already written (PRDs, RFCs,
  design docs, ADRs, acceptance criteria, API contracts, user stories). Three hard rules: every
  code change traces to a spec item, a compliance tracker is maintained as a real artifact
  (file or inline), and every non-trivial change gets an integration plan BEFORE code is
  written. Cross-language, cross-stack.
  Fires whenever the user is working from a spec — references a spec doc, asks "is this
  implemented?", asks "what's left?", or starts work on a project with a `specs/`, `docs/specs/`,
  `requirements/`, `rfcs/`, or `adrs/` directory.
  Triggers on phrases like: "implement the spec at X", "build the feature in this PRD", "is
  this spec-compliant", "check progress against the spec", "what's left in the spec", "the
  spec says X", "according to the requirements", "the acceptance criteria are", "the API
  contract is at", "the design doc specifies", "the RFC requires", "make sure we cover all the
  requirements", "track what's done", "we need a compliance tracker", "what have we shipped vs
  the spec", "I want to record progress against the spec", "plan how this fits before writing
  it", "design the integration first", "I don't want scope creep", "this isn't in the spec but
  we need it", "the spec is ambiguous about X".
  ALSO triggers in RETROSPECTIVE AUDIT mode — when code already exists and the user wants to
  reconcile it against a spec to find gaps, drift, and out-of-spec features. Trigger phrases:
  "audit this codebase against the spec", "is everything in the spec implemented", "what's
  missing from the spec", "what's been built that isn't in the spec", "build a compliance
  tracker for this existing project", "we have code and we have a spec, reconcile them",
  "we're picking up a legacy project and need to check spec coverage", "before we ship verify
  spec compliance", "the spec was updated, reconcile against current code", "what code do we
  have that isn't in any spec", "retrospective spec audit".
  Has TWO MODES:
  • FORWARD IMPLEMENTATION (building from spec) — three moments: spec discovery + tracker
    bootstrap at kickoff, integration plan before each significant change, tracker update +
    drift check after each change. End-of-session summary by default.
  • RETROSPECTIVE AUDIT (auditing existing code against spec) — nine steps: spec extraction,
    codebase reconnaissance, forward pass (spec→code per requirement with multiple search
    strategies), classification with evidence, reverse pass (code→spec to find orphans / out-
    of-spec features), test coverage check, spec drift check, ambiguity / decisions audit, and
    a prioritized findings report. The output is a populated tracker PLUS a prioritized action
    list with severities (critical / important / quality / open questions).
  Distinct from `anthropic-skills:spec-driven-dev` — that's the broader process framework
  (scope → design → decompose → execute) for any change. `spec-guard` is the narrower
  enforcement and traceability layer for projects where the spec already exists. The two pair
  well and can run together. Also distinct from `clean-code-guard` (code quality), `debug-guard`
  (broken code), and `simplify` (cleanup).
  Skip only for: changes the user explicitly labels as throwaway / exploratory ("just hack this
  up"), pure infrastructure ops with no product spec (e.g., dependency bumps with no spec
  reference), or trivial single-line edits.
---

# spec-guard

The discipline that turns "implement the spec" into "the spec is implemented, traceable,
verified, and tracked."

## The three rules

These are the rules. Every code change goes through all three.

### Rule 1 — Alignment

**Every code change traces to a spec item.** Either:

- A specific requirement ID from the spec (`R3`, `§2.4`, `US-12`, whatever IDs the spec uses),
  OR
- An **explicitly recorded** out-of-spec decision with justification, captured in the tracker.

If a change doesn't satisfy either, it doesn't ship in this session. It becomes a follow-up
issue, a spec amendment, or it's dropped.

### Rule 2 — Recording

**A compliance tracker is maintained as a real artifact** — either inline in the conversation
(when the user wants ephemeral) or persisted to a file (default: `SPEC-COMPLIANCE.md` at the
repo root, or whatever the project already uses).

The tracker isn't a "nice to have" or "I'll write it up after." It's updated *as* work happens,
because that's when the information is correct.

See [`references/tracker.md`](./references/tracker.md) for the template and the discipline of
maintaining it.

### Rule 3 — Planning

**Every non-trivial change gets an integration plan BEFORE code is written.** The plan
captures:

- Which spec items it addresses
- Which existing code surfaces it touches
- Which new abstractions it introduces (and where they fit)
- What dependencies must exist first
- What risks / conflicts it has with other work
- The test plan tied to acceptance criteria

"Non-trivial" = more than ~20 lines of new code, touches multiple files, or introduces a new
concept. One-line edits don't need a plan; a new module does.

See [`references/integration-plan.md`](./references/integration-plan.md) for the template.

---

## Two modes

The skill operates in one of two modes — pick at kickoff:

- **Forward implementation** — you're building from the spec. The workflow below (three
  moments) applies.
- **Retrospective audit** — code already exists; the spec exists; no tracker (or stale one)
  exists; you need to reconcile them. **See [`references/audit-mode.md`](./references/audit-mode.md)
  for the nine-step audit playbook.**

Both modes share the same tracker format, anti-patterns, and discipline. They differ in
*shape* — forward mode plans then builds; audit mode finds then records.

If unsure which mode the user wants, ask: "Are we building this fresh, or auditing existing
code against the spec?"

---

## Forward implementation workflow

### Moment 1 — Spec discovery and tracker bootstrap (start of session)

When a spec-driven task begins, do these in order:

1. **Find the spec.** Where does it live? `docs/specs/`, `rfcs/`, a Notion link, a PRD path
   in the chat. If the spec source isn't obvious, **ask the user before reading anything else.**
2. **Read the spec in full.** Not the first section. The whole thing. Including acceptance
   criteria, non-functional requirements, edge cases, out-of-scope notes.
3. **Extract every requirement.** Build the initial tracker — see
   [`references/tracker.md`](./references/tracker.md). Use the spec's own IDs if it has them;
   generate IDs (`R1`, `R2`, ...) if not.
4. **Confirm scope for this session.** Ask: "Which items are we doing now?" Default if the user
   doesn't say: top-priority unstarted items. Mark in-scope items explicitly.
5. **Confirm tracker location.** Default to `SPEC-COMPLIANCE.md` at the repo root unless the
   project has an existing convention.

See [`references/spec-discovery.md`](./references/spec-discovery.md) for guidance on common spec
formats (PRDs, RFCs, design docs, ADRs, user stories, OpenAPI contracts).

### Moment 2 — Integration plan (before each significant change)

Before writing more than ~20 lines of code, produce an integration plan. State it in the
conversation; it goes into the tracker's plan section.

The plan is the cheapest refactor. Get a nod from the user before implementing. This is where
scope creep dies and design issues surface.

### Moment 3 — Tracker update + drift check (after each change)

After applying a change:

1. **Update the tracker.** Status (Not started → In progress → Done → Verified), evidence
   (file paths, test names, commit refs), and any decisions made.
2. **Drift check** — quick scan:
   - Did this change implement something *not* in the spec? Record it as out-of-spec.
   - Did the spec require something this change *should have* covered but skipped? Note the
     gap.
   - Did the spec have ambiguity that needed resolving? Record the decision.

At the end of the session, produce a **progress summary**: items completed, items in progress,
items blocked, out-of-spec changes (with justification), open questions, what's next.

---

## Retrospective audit mode (summary)

When the user wants to audit existing code against a spec — to find gaps, drift, and
out-of-spec features — switch to audit mode. Full nine-step playbook in
[`references/audit-mode.md`](./references/audit-mode.md).

The audit produces two artifacts:

1. **A populated tracker** — every spec requirement classified with status (⬜ / 🟡 / ✅ / 🟦 /
   ❌ / ➖) and evidence (file paths + test names + commit refs). Plus an Out-of-spec table
   listing code that doesn't trace to any spec item, an Open Questions table for ambiguities,
   and a Decisions log for implicit decisions surfaced.

2. **A prioritized findings report** — categorized by severity:
   - **Critical** — blocks shipping (unimplemented MUST requirements; security/data drift)
   - **Important** — should fix before release (partial implementations; minor drift; risky
     out-of-spec)
   - **Quality gaps** — missing tests, undocumented dependencies, candidates for removal
   - **Open questions** — needs user input before any action

The audit's value is in the **evidence** — every claim ties to a file/test/commit. "Looks
implemented" is not a finding; "implemented at `path/file.ts:42`, tested by `tests/x.spec.ts`"
is.

After an audit, the tracker becomes the baseline for ongoing work — forward implementation
mode picks up from where the audit left off.

---

## The compliance tracker (summary)

The artifact. Full template and discipline in
[`references/tracker.md`](./references/tracker.md). Skeleton:

```markdown
# Spec compliance: <feature name>

**Spec source**: `docs/specs/feature-x.md` (rev <version-or-date>)
**Last updated**: 2026-05-21 by <session>

## Requirements

| ID | Requirement                       | Spec ref | Status | Evidence                              |
|----|-----------------------------------|----------|--------|---------------------------------------|
| R1 | Users can create a session        | §2.1     | ✅ Done | `app/api/sessions.ts` · `tests/sessions.test.ts::create` |
| R2 | Sessions expire after 24h         | §2.3     | 🟡 In progress | `app/services/session.ts` (TTL done; expiry job pending) |
| R3 | Audit log entry per action        | §4.2     | ⬜ Not started |                                       |
| R4 | Rate limit: 100 req/min per user  | §2.5     | ❌ Blocked  | Awaiting decision on window strategy |

## Out-of-spec changes

| ID | Change                          | Justification                       | Decided by  | Tracker note |
|----|---------------------------------|-------------------------------------|-------------|--------------|
| X1 | Added Redis for rate-limit state | Required by R4; not specified      | user 5/21   | Spec needs update |

## Open questions

| ID | Question                                | Spec ref | Resolution                |
|----|------------------------------------------|----------|---------------------------|
| Q1 | What's the rate-limit window unit?       | §2.5     | Pending user decision     |

## Decisions log

| ID | Decision                                 | Why                                 | When  |
|----|------------------------------------------|-------------------------------------|-------|
| D1 | Use JWT for session tokens, not opaque   | Existing stack uses JWT (cohesion)  | 5/21  |
```

**Status legend:**
- ⬜ Not started
- 🟡 In progress
- ✅ Done (implemented, not yet verified against acceptance criteria)
- 🟦 Verified (acceptance criteria met, with evidence)
- ❌ Blocked
- ➖ Deferred (explicitly out of this milestone)

---

## The integration plan (summary)

Full template and worked examples in
[`references/integration-plan.md`](./references/integration-plan.md). Skeleton:

```markdown
**Change**: <one-line summary>

**Spec items addressed**: R1, R3

**Existing code surfaces touched**
- `app/models/user.py` — User model gains `last_session_at` field
- `app/api/sessions.ts` — new POST /sessions handler

**New abstractions**
- `SessionService` — owns lifecycle (create / renew / expire). Lives in `app/services/`.

**Dependencies (must exist first)**
- R0 (User model) — ✅ Done
- DB migration for `sessions` table — needs writing as part of this change

**Risks / conflicts**
- Conflicts with in-flight feature on `users` table (rebase needed)
- Token refresh logic affects existing `/refresh` endpoint — verify backward compat

**Test plan (tied to acceptance criteria)**
- R1 AC1 (create returns 201 with token) → `tests/sessions/test_create.py::test_create_returns_token`
- R1 AC2 (token is JWT) → same file::test_token_is_jwt
- R3 AC1 (audit row created per action) → `tests/audit/test_session_audit.py`
```

---

## The 10 anti-patterns of vibe-spec work

Full catalog with examples in [`references/anti-patterns.md`](./references/anti-patterns.md).

1. **Spec drift** — implementing what feels natural instead of what the spec says.
2. **Silent scope creep** — adding things not in the spec without recording why.
3. **The "I'll track it later" lie** — never tracking. The tracker happens *as* work happens or
   it doesn't happen.
4. **The vague-acceptance** — marking a requirement done without pointing to the code and test
   that prove it.
5. **The verbal spec** — relying on chat history or memory instead of the canonical document.
6. **The implicit decision** — making a design choice the spec was silent on without recording
   it.
7. **The cherry-pick** — implementing the easy 80% of the spec and quietly skipping the hard
   20%.
8. **The ahead-of-spec** — coding ahead of where the spec is settled; spec changes invalidate
   your work.
9. **The plan-as-narration** — writing the integration plan *after* implementing, as a
   description of what you did, defeats its purpose.
10. **The spec-vs-code drift** — code evolves, spec doesn't. Now the canonical doc is the code
    nobody verifies. Update the spec or amend it explicitly.

---

## Handling spec ambiguity, gaps, and conflicts

Specs are rarely perfect. When you hit one of these:

- **Ambiguity** ("the spec says X, but X could mean two things") — record as an open question
  in the tracker, surface to the user, wait for a decision, record the decision.
- **Silence** (the spec doesn't address something you need to decide) — propose the decision,
  surface to the user, record it in the decisions log.
- **Contradiction** (the spec says X in one place and ¬X in another) — surface immediately;
  this is a spec bug. Get the user to resolve, then update the spec.
- **Real-world mismatch** (the spec says X but real conditions make X impossible or wrong) —
  surface, propose an amendment, get sign-off, record as out-of-spec until the spec is updated.

The pattern: **surface, decide, record.** Never silently resolve ambiguity in code — that's how
the spec and the implementation drift apart.

---

## Output format

When this skill is active, structure responses like this:

### At session start:

```
**Spec**: `<path>` (rev <date>)
**Scope this session**: R1, R3, R5

I've extracted N requirements into [`SPEC-COMPLIANCE.md`](./SPEC-COMPLIANCE.md). Before
implementing R1, here's the integration plan:

<integration plan>

OK to proceed?
```

### Before each significant change:

The integration plan template, with the spec items it addresses called out by ID.

### After each change:

```
✅ R1 → Done. Evidence: `app/api/sessions.ts` · `tests/sessions.test.ts::create_returns_201`
🟡 R3 → In progress. Audit table created (`migrations/0042.sql`); handler not yet wired.

Tracker updated: SPEC-COMPLIANCE.md
```

### At session end:

```
**Session summary**

Done this session:
- R1 (create session) ✅
- R2 (24h expiry) ✅

In progress:
- R3 (audit log) 🟡 — handler wired, test pending

Blocked:
- R4 (rate limit) ❌ — pending decision on window strategy (Q1)

Out-of-spec changes:
- X1: added Redis dependency for R4 prerequisite (recorded)

Decisions made:
- D1: JWT for session tokens (cohesion with existing stack)

Up next: finish R3 test, resolve Q1, then R4.
```

---

## What this skill is NOT

- **Not a spec writer.** This skill enforces compliance with a spec that already exists. If you
  need to *create* a spec, use a different tool (or just write one — many of the principles
  apply in reverse).
- **Not a process framework.** That's `anthropic-skills:spec-driven-dev`. Run both when you
  need both — they reinforce each other.
- **Not a blocker for trivial work.** A typo fix doesn't need an integration plan. Use
  judgment.
- **Not a replacement for code review.** The tracker shows *what* shipped vs *what* was
  required; it doesn't verify the code is good. Pair with `clean-code-guard` for that.

---

## See also

- [`references/tracker.md`](./references/tracker.md) — compliance tracker template, status
  taxonomy, evidence discipline, how to maintain it across sessions
- [`references/integration-plan.md`](./references/integration-plan.md) — integration plan
  template with worked examples; what counts as "non-trivial"
- [`references/spec-discovery.md`](./references/spec-discovery.md) — finding and parsing specs
  across common formats (PRDs, RFCs, design docs, ADRs, user stories with given/when/then,
  OpenAPI / GraphQL contracts, ticket bodies)
- [`references/audit-mode.md`](./references/audit-mode.md) — retrospective audit playbook for
  reconciling existing code against a spec. Nine-step workflow, search strategies for
  finding implementing code, classification rules, reverse pass to find out-of-spec
  features, test coverage and drift checks, and a prioritized findings report template
- [`references/anti-patterns.md`](./references/anti-patterns.md) — the 10 vibe-spec patterns to
  catch and avoid
