# Content structure — the ten sections

What goes in each section, what doesn't, how to phrase items, what to cut.

The order matters (Pyramid Principle — see `exec-comms.md`). Most-important / most-summary
content first; detail last.

---

## 1. Executive summary

**Length**: 3-5 bullet points, each one sentence.
**Audience**: C-level / board / busy exec who reads this and nothing else.

### What goes here

- The single most important thing that happened this period (BLUF)
- Overall status (🟢 / 🟡 / 🔴) with one-line justification
- The thing that needs the reader's attention or action (if any)
- The thing on the horizon they should know about (if relevant)

### What doesn't

- Technical detail of any kind
- Names of files, classes, libraries, services
- Lists of every PR or commit
- Hedged language ("things are going well, mostly")

### Template

```markdown
## Executive summary

- **Status: 🟡 Amber.** On track to ship MVP by 2026-06-01 if one decision lands this week.
- **Shipped**: Session creation, expiry, and refresh are live — the auth surface frontend
  needs is in place.
- **Risk**: Rate limiting (R4) blocked on a window-strategy decision (Q1). Without that
  decision by Friday, launch date slips by 3 days.
- **Decision needed**: <user>, please review Q1 in `SPEC-COMPLIANCE.md` and decide.
- **Next milestone**: Complete audit logging (R3) and rate limiting (R4) → GA-ready by EOM.
```

### Quality bar

If a board member read just this section, would they:
- Know the project's state? (Yes / Amber on the table above)
- Know what to do? (Yes / decide Q1)
- Know what to expect? (Yes / GA EOM if decision lands)

If any answer is no, rewrite.

---

## 2. Headline metrics

**Length**: 4-6 KPIs as cards/numbers.
**Audience**: Manager wanting a numeric snapshot in 30 seconds.

### What goes here

Numbers that matter for the project's outcome — not vanity metrics. Each one with a trend
indicator vs. the previous period.

### Suggested metrics

Pick 4-6 that matter for *this* project. Don't show all of them.

| Metric                          | Why it matters                                 |
| ------------------------------- | ---------------------------------------------- |
| Spec compliance %               | Headline number for spec-driven projects       |
| Spec items done / total         | Concrete progress                              |
| Spec items in progress          | Work in flight                                 |
| Spec items blocked              | RED indicator if > 0                           |
| Commits / PRs this period       | Activity level                                 |
| Days to next milestone          | Time pressure                                  |
| Test pass rate                  | Quality signal                                 |
| Open critical bugs              | Hygiene signal                                 |
| Lead time to merge              | Team velocity                                  |
| Deployment frequency            | Delivery velocity                              |

Avoid:
- LOC (lines of code) — measures activity not progress
- Number of meetings — irrelevant
- Bytes shipped, story points completed — usually proxies that mislead

### Trend indicator

Every metric gets a trend: ▲ +X, ▼ -X, ◆ no change. Compared to the previous report period
of the same length.

### Template

```
| Metric                | Value     | Trend  |
| --------------------- | --------- | ------ |
| Spec compliance       | 75%       | ▲ +25% |
| Items done / total    | 9 / 12    | ▲ +3   |
| Items in progress     | 2         | ▲ +1   |
| Items blocked         | 1         | ◆ same |
| Commits this period   | 47        | ▲ +15  |
| PRs merged            | 8         | ▲ +3   |
| Test pass rate        | 98%       | ◆ same |
```

---

## 3. Overall status

**Length**: 🟢 / 🟡 / 🔴 indicator + one-line justification.
**Audience**: Anyone scanning.

### What goes here

Just the indicator and the *because*. No long explanation.

### Examples

- **🟢 Green** — On track for EOQ; no outstanding decisions; no blockers.
- **🟡 Amber** — On track if Q1 decision lands by Friday; otherwise 3-day slip.
- **🔴 Red** — Blocked on R4 (rate limiting) and R10 (admin tooling); ship date at risk by 2+
  weeks until resolved.

### Honesty check

Per `exec-comms.md`: green is rare in honest reporting. If you have *any* blocker, *any*
outstanding decision affecting ship date, or *any* significant unknown — you're amber at
minimum.

---

## 4. What shipped this period

**Length**: 3-7 items (group / merge / cut if more).
**Audience**: Manager and exec; this is the "delivery" section.

### What goes per item

Each shipped item gets:

- **Title** — feature name in user-facing language (not engineer-facing)
- **What** — one sentence on what the user can now do
- **Why it matters** — one sentence on business impact (the "so what")
- **Tech** — one line for engineers (file paths, key files / classes / migrations)
- **Evidence** — spec ID or commit ref or PR number
- **Spec ref** — `§2.1` or `R1`

### Template

```markdown
### Session creation API

- **What**: Users can create authenticated sessions via the new login flow.
- **Why it matters**: Unblocks the entire frontend authentication surface — UI team can now
  begin login integration without waiting on us.
- **Tech**: `app/api/sessions.ts`, `app/services/session.ts`, migration `0042_sessions.sql`.
- **Evidence**: Spec R1 → PR #128 (merged 2026-05-20); tested by `tests/sessions.test.ts`
  (5 scenarios, all passing).
- **Spec ref**: `docs/specs/auth.md §2.1`
```

### Grouping

If you have 8+ shipped items, group by theme:

```markdown
### Authentication (3 items)
- Session creation, expiry, refresh — full happy-path auth flow live.

### Infrastructure (2 items)
- Redis cache, audit log table — supporting work for upcoming features.
```

### What to cut

- Pure refactors with no user/business impact (mention in appendix)
- Internal tooling improvements (unless they shipped a customer-facing speedup)
- Documentation updates (unless the audience cares specifically about docs)

---

## 5. In progress

**Length**: 3-7 items.
**Audience**: Manager wanting to know what's in flight.

### What goes per item

- **Title** + spec ref
- **% complete** — rough but honest (25 / 50 / 75 — don't false-precision to 67%)
- **What's left** — one line on the remaining work
- **Expected ship** — date or relative ("end of week," "next sprint")
- **Risk** — anything that could push the date

### Template

```markdown
### R3 — Audit log per action (75% complete)

- **What's left**: handler wiring for write endpoints (8 of 12 done)
- **Expected ship**: Thursday 2026-05-23
- **Risk**: low; pattern is established, remaining 4 are mechanical
```

### Percent complete — honesty rules

- 0-25%: just started; scope still being clarified
- 25-50%: design done, implementation underway
- 50-75%: most code written, integration and edge cases remain
- 75-90%: feature works in happy path; testing, docs, polish remain
- 90-99%: blocked on review / QA / final acceptance
- 100%: move to Shipped section

**Don't sit at 90% for three weeks.** If it's been there a while, either it's blocked
(move to section 6) or the scope was wrong.

---

## 6. Blocked / decisions needed

**Length**: 1-5 items. Should be VERY visible in the report (red callout in HTML).
**Audience**: The decision maker. This is the most important section if it has anything in it.

### What goes per item

- **What's blocked**
- **Why** (with the specific question or dependency)
- **Who decides** (named person, not "the team")
- **By when** (specific date)
- **Impact of delay** (cost of waiting, in concrete terms)

### Template

```markdown
### R4 — Rate limiting (BLOCKED)

- **What's blocked**: Implementation of rate limiting (`POST /sessions`, all auth endpoints).
- **Why**: Outstanding question Q1: should we use fixed-window or sliding-window? See
  `SPEC-COMPLIANCE.md`.
- **Who decides**: <user> (product owner) with input from platform team.
- **By when**: Friday 2026-05-23.
- **Impact of delay**: Each day of delay = one day slip in GA launch.
```

### The decision template

If the decision has options, lay them out:

> "**Q1** — Rate-limit window strategy.
> - Option A (fixed window): simpler, can ship next week. Edge case: 200/min possible at
>   window boundary.
> - Option B (sliding window): more accurate, requires Redis sorted sets, ships 2 days later.
> - Recommendation: Option A for MVP; revisit post-launch if needed."

The reader should be able to decide without going to another doc.

---

## 7. Decisions made this period

**Length**: 3-7 items.
**Audience**: Historical record + the RAG.

### What goes per item

- **Decision** — what was decided
- **Why** — one-line rationale
- **When** — date
- **Reversibility** — easy / medium / hard (informs how to flag risk)
- **Owner** — who decided

### Template

```markdown
- **D1**: Use JWT for session tokens (not opaque). _Cohesion with existing stack._ Decided
  2026-05-21 by <user>. Reversibility: hard (clients depend on token format).
- **D2**: No webhook on session expiry. _Avoids noise; expiry is internal._ Decided
  2026-05-21 by <user>. Reversibility: easy.
```

### Why include this

Three reasons:
1. **Audit trail** — six months later, someone asks "why did we do X?" The record has the
   answer.
2. **RAG value** — the RAG can answer "what decisions have we made about auth?"
3. **Forces thinking** — if you can't write the rationale in one line, the decision needs
   more thought.

---

## 8. Open questions

**Length**: 1-5 items.
**Audience**: Whoever can resolve them.

### What goes per item

- **The question**
- **What it blocks** (which spec items / dates)
- **Who needs to answer**
- **When the answer is needed**

### Template

```markdown
- **Q1**: Rate-limit window — fixed or sliding? Blocks R4. Needed from <user> by Fri.
- **Q2**: Do mobile clients need session push on revoke? Blocks R10. Needed from product by
  next sprint.
```

### Differentiation from Section 6

Section 6 (Blocked) is about *current* work that's stuck.
Section 8 (Open questions) is about *future* work that needs answers before it can start.

Often they reference each other.

---

## 9. Risks

**Length**: 3-7 items.
**Audience**: Anyone responsible for delivery.

### What goes per item

- **Risk** — what could go wrong
- **Severity** — 🟢 low / 🟡 medium / 🔴 high (or use words)
- **Likelihood** — low / medium / high
- **Mitigation** — what we're doing about it
- **Owner** — who's watching it

### Template

```markdown
| Risk                                          | Severity | Likelihood | Mitigation                                | Owner   |
|-----------------------------------------------|----------|------------|-------------------------------------------|---------|
| Backend ship date hold required for FE cutover | 🟡 med    | medium     | Coordinate ship; tentative 5/24           | <user>  |
| Redis dependency new to ops team              | 🟡 med    | low        | Runbook drafted; on-call training planned | <ops>   |
| Rate limit window unknown (Q1)                | 🔴 high   | high       | Decision targeted Fri                     | <user>  |
```

### Common bad risks

- "Things could go wrong." → not actionable.
- "Team is busy." → not specific.
- "Tech debt." → too broad.

Each risk should be **specific**, **owned**, and have a **mitigation**. If a risk has no
mitigation, surface that explicitly: "Mitigation: none yet — needs discussion."

---

## 10. Next period plan

**Length**: 3-5 items. What you'll have done by next report.
**Audience**: Everyone — sets expectations for the next report.

### What goes per item

- The outcome (not the activity)
- The spec ref if applicable
- A rough date or "by next report"

### Template

```markdown
- Resolve Q1; unblock R4; ship rate limiting (target 2026-05-26)
- Complete R3 audit logging (target 2026-05-23)
- Begin R5 token refresh (target start 2026-05-26)
- Pre-launch security review (target 2026-05-30)
```

### Outcome-not-activity

Bad: "Spend time on rate limiting." (activity)
Good: "Ship rate limiting by Friday." (outcome)

The next report verifies against this plan. **The previous report's next-period plan is the
current report's accountability check** — call out items that did vs. didn't land.

---

## Appendix — raw activity

**Length**: as long as needed; not summarized.
**Audience**: ICs, the curious, the future.

### What goes here

- Full commit list with hashes
- Full PR list
- Full issue list
- File-level activity (which files were touched most)
- Test changes (added / removed / changed)
- Dependencies added/removed/updated

### Format

Collapsible in HTML; under a `## Appendix` heading in Markdown so RAG can still index it.

This is the data dump. The report above is the *narrative on top of* this data dump.

---

## Putting it together — the narrative thread

The sections aren't independent. They tell a story top to bottom:

1. **Exec summary** — sets the answer
2. **Metrics** — gives the numeric backing
3. **Status** — confirms the headline
4. **Shipped** — proves the answer with deliveries
5. **In progress** — shows what's continuing
6. **Blocked** — surfaces what's at risk (most important section if non-empty)
7. **Decisions** — records the calls made
8. **Questions** — surfaces what's still uncertain
9. **Risks** — names what could go wrong
10. **Next** — sets up the next report

A reader who reads all 10 in order gets a complete picture. A reader who reads only section 1
gets the conclusion. A reader who reads 1 + 4 + 6 + 10 gets the "what shipped, what's
blocked, what's next" view they probably want.

The pyramid lets each reader find their natural stopping point.
