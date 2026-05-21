# Retrospective audit mode

`spec-guard` has two modes:

- **Forward implementation** — building from a spec. Default workflow in `SKILL.md`.
- **Retrospective audit** — code already exists, spec already exists, no tracker (or stale one). The
  work is to reconcile the two, surface gaps, and produce a compliance tracker that reflects
  reality.

This file is the playbook for the second case.

---

## When to use this mode

Trigger phrases:

- "audit this codebase against the spec"
- "is everything in the spec implemented?"
- "what's missing from the spec?"
- "what's been built that isn't in the spec?"
- "build a compliance tracker for this existing project"
- "we have code and we have a spec — reconcile them"
- "we're picking up a legacy project; check spec coverage"
- "before we ship, verify spec compliance"
- "the spec was updated; reconcile against current code"
- "what code do we have that isn't in any spec"

Common situations:

- Inheriting a project / new team member onboarding
- Pre-release compliance check
- Resuming after a long break — what's the actual state?
- Spec was updated, code wasn't — what diverged?
- Auditor or compliance officer needs a snapshot
- The original tracker fell behind reality

---

## The audit workflow

Steps in order. Each one produces real output in the tracker.

### Step 1 — Spec discovery and extraction

Same as forward mode. See [`spec-discovery.md`](./spec-discovery.md).

Outcome: every requirement extracted into the tracker with status `⬜ Not started` (initial).
Acceptance criteria expanded for each.

If multiple specs exist (PRD + OpenAPI + ADRs + Gherkin), gather them all and note each spec
source on each tracker row.

### Step 2 — Codebase reconnaissance

Before going requirement-by-requirement, get a map of the code:

- **Entry points** — HTTP routes (`routes`, `controllers`, `pages/api`, `app/api`); CLI
  entrypoints; queue consumers; cron jobs; event handlers.
- **Domain code** — `services/`, `domain/`, `core/`. Where the verbs of the spec are likely
  to live.
- **Models** — schema files, ORM models, type definitions. Where the nouns live.
- **Tests** — `tests/`, `__tests__/`, `spec/`. Often the cleanest description of intended
  behavior.
- **Recent activity** — `git log --since="<spec date>" --stat` shows what's been touched
  since the spec was written. Helps prioritize where to look.

You don't need to read everything. You need a map so you know *where* to look for each
requirement.

### Step 3 — Forward pass: spec → code (per requirement)

For each requirement, find the implementing code. Use multiple search strategies in
parallel:

| Strategy                            | What it catches                                            |
| ----------------------------------- | ---------------------------------------------------------- |
| Symbol search (grep / ripgrep)      | Names from the requirement: verbs, nouns, IDs              |
| Path search                         | Files/modules named after the concept (`audit/`, `auth/`)  |
| Commit message grep                 | `git log --all --grep="R3"` if commits cite spec IDs       |
| Comment grep                        | `// R3:` or `# Implements R3` style references             |
| Test name search                    | Tests often describe the requirement in plain English      |
| Route table read                    | For API requirements: find the endpoint                    |
| Config / env scan                   | Feature flags, settings that gate the feature              |
| Diff against last known spec rev    | If tracker has a recorded rev, see what's changed          |

The first match isn't always the whole implementation. Follow call chains: the route handler
→ the service → the data layer. The requirement is met when *all* layers exist and connect.

### Step 4 — Classify each requirement

Based on what step 3 found, assign a status with explicit evidence:

| Finding                                                          | Status        | Tracker action                                |
| ---------------------------------------------------------------- | ------------- | --------------------------------------------- |
| Implementation found · all ACs covered · tests pass              | 🟦 Verified   | Evidence column = file paths + test names     |
| Implementation found · all ACs covered · no tests                | ✅ Done       | Evidence + Notes: "no automated test — risk"  |
| Implementation found · partial AC coverage                       | 🟡 In progress | Evidence + AC checklist showing which met    |
| Implementation found · diverges from spec                        | 🟡 In progress | Evidence + Notes: "diverges on X — see Q/D" |
| Nothing found in code                                            | ⬜ Not started | Notes: confirmed not implemented after audit |
| Found but disabled / behind off feature flag                     | ⬜ Not started | Notes: code exists but inactive               |
| Conflicts irreconcilably with another part of the code           | ❌ Blocked    | Notes: nature of the conflict                 |
| Explicitly out of this release                                   | ➖ Deferred   | Notes: where it's tracked (issue link)       |

**Always populate the Evidence column on this pass.** A retrospective audit's value is the
evidence — without it, the tracker is just speculation.

### Step 5 — Reverse pass: code → spec (find orphans)

This is the step most audits skip. It's where the surprises live.

Walk the **main entry points** (routes, public APIs, cron jobs, queue consumers) and for each,
ask: **which spec item does this implement?**

- Crossreference the tracker. Most entry points should map to a known requirement.
- Orphans (entry points with no matching tracker row) are **out-of-spec features**. Record
  them in the Out-of-spec table with:
  - What it does (one line)
  - Best guess at justification (history, commits, code comments)
  - Status: needs review (mark "decided by: TBD" until the user reviews)

You don't need to walk every file — focus on **public surfaces** and **anything that
introduces a side effect** (DB writes, network calls, file I/O, event emission, background
work). Internal helpers don't usually need a spec mapping.

### Step 6 — Test coverage check

For every requirement marked ✅ Done or 🟦 Verified:

1. Find the test(s) that exercise its acceptance criteria.
2. Verify the test isn't:
   - Skipped (`.skip`, `xit`, `@pytest.mark.skip`, `t.Skip`)
   - Trivial (asserts only that the function exists, not that it works)
   - Outdated (last touched before a significant change to the implementation)

If a requirement claims to be Done but has no test that exercises it → status drops to ✅ Done
with a "test gap" note (not 🟦 Verified). Test gaps are themselves findings.

### Step 7 — Spec drift check (per requirement)

For each implemented requirement, compare the **acceptance criteria** in the spec against the
**actual behavior** of the code:

- Does the function return what the spec says?
- Does the endpoint accept what the spec says?
- Are the side effects (audit log, events, metrics) what the spec specifies?
- Are the error cases handled as specified?

Drift is common in projects that have been live for a while. When you find drift, classify:

- **Spec is right, code is wrong** → bug. File as a finding with severity.
- **Code is right, spec is stale** → spec amendment needed. File as a finding ("spec out of
  date").
- **Both have moved; correct answer is somewhere in between** → escalate to user for decision.

### Step 8 — Ambiguity and decisions audit

Even if the code is "right," there may be implicit decisions that the spec didn't make:

- The spec says "limit retries"; the code uses 5 — was that decided anywhere?
- The spec says "log errors"; the code uses ERROR level — that may be a decision worth
  recording.

For each implicit decision you find that's not in the Decisions log, file it. Don't
retroactively claim someone "decided" it — note "discovered during audit, decision rationale
not recorded" and let the user fill in or accept.

### Step 9 — Produce the audit report

The output of a retrospective audit isn't just the populated tracker — it's a **prioritized
findings report** that tells the user what to do next.

See the template below.

---

## The audit report template

```markdown
# Spec compliance audit: <feature or release>

**Audit performed**: 2026-05-21
**Auditor**: <session>
**Spec sources**:
- Product: `docs/specs/feature-x.md` (rev 2026-05-15)
- API contract: `openapi.yaml` (paths under `/sessions`)
- ADRs: `docs/adrs/0003-jwt.md`, `docs/adrs/0007-audit.md`

**Codebase**: `<repo>@<commit-sha>`

## Top-line summary

- **12 requirements** in spec
- **9** implemented and matching spec (R1-R6, R8, R9, R12)
- **1** partially implemented (R7 — missing AC3)
- **2** not implemented (R10, R11)
- **3** out-of-spec features detected (X1-X3)
- **4** implemented requirements lack automated tests (R5, R8, R9, R12)
- **2** spec items have implementation drift (R2, R6)
- **3** open questions need user input

**Compliance score** (rough): 9/12 ≈ 75% verified; 11/12 ≈ 92% with code present.

## Findings (prioritized)

### Critical — blocks shipping
1. **R10 (Admin can revoke any session)** — not implemented. Spec marks this MUST. Required
   for admin tooling. Estimate: ~1 day. → See action item A1.
2. **R11 (Audit log entry per action)** — not implemented. Spec marks this MUST for
   compliance. → A2.
3. **R2 drift (session expiry)** — spec says 24h absolute; code implements 24h idle
   (refreshes on use). Behavior difference for long-lived users. → A3 (decide which is
   correct).

### Important — should fix before release
4. **R7 partial** — AC1 and AC2 implemented; AC3 (audit row on revoke) missing. → A4.
5. **R6 drift (token refresh)** — spec says token reissued on refresh; code reuses same
   token, extends expiry. Minor security implication. → A5.
6. **Out-of-spec X2 (Redis cache)** — undocumented infrastructure dependency. → A6
   (document in spec or remove).

### Quality gaps — fix in next milestone
7. **Test coverage** — R5, R8, R9, R12 implemented without automated tests. Manual smoke
   only. → A7.
8. **Out-of-spec X1 (admin debug endpoint)** — appears unused. → A8 (candidate for
   removal).
9. **Out-of-spec X3 (deprecated /v1 route)** — still live. → A9 (deprecation path).

### Open questions for user
10. **Q1**: Should we standardize on absolute vs idle session expiry? (blocks A3)
11. **Q2**: Is Redis a sanctioned dependency? (blocks A6)
12. **Q3**: Was the admin debug endpoint intentional? (blocks A8)

## Compliance tracker (full)

<the SPEC-COMPLIANCE.md tracker with every row populated>

## Recommended next steps

1. Resolve Q1, Q2, Q3 with the user (~15 min)
2. Pick up A1, A2 (critical gaps)
3. Decide on A3, A5 (spec drift) → file spec amendments or code fixes
4. Add tests for A7
5. Clean up A6, A8, A9 in the next housekeeping pass

```

---

## Practical tips

### Don't try to audit everything at once

For a large codebase, **scope the audit explicitly**:
- One feature / epic at a time
- One service / module at a time
- One spec document at a time

Doing the whole codebase in one shot leads to a giant report nobody reads. A focused audit
that produces a 1-page findings list is more useful.

### Use the tracker's "Last updated" to show recency

The audit isn't just for the moment — it becomes the baseline tracker going forward. When
future sessions resume work, they pick up from this state. Make sure the tracker's metadata
reflects this (Last updated, Auditor, Spec rev).

### Surface, don't fix (in the audit pass)

The audit's job is to **find and record**, not to fix. Resist the urge to fix small things
mid-audit:

- An obvious bug → record it as a finding; let the user decide priority
- A drift between spec and code → record both states; let the user decide which is canonical
- A missing test → record it; don't write the test during the audit

Fixing during audit muddies the report and tempts you to skip the systematic part. **Audit
first, fix in a separate pass.**

### Be honest about audit uncertainty

A retrospective audit is an inference from code. You can be wrong:
- Code you didn't find may still exist (large codebase, unusual naming)
- A test that "passes" may not actually exercise the requirement
- Drift may be intentional and undocumented

For uncertain findings, mark them explicitly:
- "Likely not implemented (searched X, Y, Z)" rather than "Not implemented"
- "Test exists but unclear whether it exercises AC2" rather than "Verified"
- "Code appears to diverge from spec; needs human review" rather than "Drift confirmed"

Audits build user trust when they're honest about their limits.

### When the spec is the problem

Sometimes the audit reveals the **spec is stale, vague, or wrong** more than the code is.
That's a finding too:

- Spec says "fast" without a number → not a verifiable requirement; record as ambiguous
- Spec describes a UI that no longer exists → spec needs update
- Spec contradicts itself → record the contradiction

Don't try to write a better spec mid-audit. File the finding, propose an amendment, let the
user lead.

---

## Audit-specific anti-patterns

In addition to the 10 in `anti-patterns.md`:

### A. The "Verified by reading the code" claim

Marking something 🟦 Verified because you read the code and it looks right. Verified means a
test (or a documented manual procedure) confirms the acceptance criteria. Reading code is
inference, not verification.

### B. The retroactive plan

Writing an integration plan for code that already exists, as if the audit were a forward
implementation. The audit's artifact is the tracker + findings, not a plan. Save plans for
the follow-up work that *fixes* what the audit found.

### C. The "everything's fine" report

If your audit finds zero issues, either the project is exceptional, or the audit was
shallow. Most audits find at least 2-3 things. Re-check what you skipped before declaring
all clear.

### D. The "I'll do a deeper audit later" deferral

If the audit is worth doing, do it properly. A surface-level "everything seems to be there"
audit is worse than no audit, because it creates false confidence.

### E. The audit-without-evidence

Producing a tracker where most Evidence cells are empty or vague ("see code"). The audit's
*entire value* is the evidence column. Without it, the tracker is unverifiable speculation.
