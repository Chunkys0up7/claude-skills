# Executive communication — the principles

The methodologies behind the structure `manager-update` enforces. Read this when the skill
isn't producing the *quality* of report you want — the rules need to land before the templates
do.

---

## The Pyramid Principle (Barbara Minto)

The single most important framework. Used at McKinsey since the 1970s; used at every top-tier
strategy consultancy and almost every well-run product org.

### The three rules

1. **Ideas at any level must be summaries of the ideas grouped below them.** Every parent
   statement is the synthesis of its children, not just one of them.
2. **Ideas in each grouping must be of the same kind.** Don't mix "things we shipped" and
   "things we decided" in one list.
3. **Ideas in each grouping must be in a logical order.** Time / structure / importance —
   pick one per grouping and stick to it.

### Why it works for status reports

A status report is read by 5 different audiences with 5 different attention budgets:

- **Board**: reads the headline only — 30 seconds
- **Exec**: reads the exec summary — 2 minutes
- **Manager**: reads sections 1-6 — 5 minutes
- **Lead**: reads everything except appendix — 10 minutes
- **IC**: reads the appendix and the linked PRs — 30+ minutes

The pyramid makes one document work for all five — each layer is a complete summary of what's
below. **The reader can stop at any level and have the right understanding for their level.**

### Application checklist

For each section in the report, ask:
- Does the section heading summarize what's in the section? (Rule 1)
- Are all items in this section the same kind of thing? (Rule 2)
- Are the items in an order I can name (by priority? by date? by stage?)? (Rule 3)

If any answer is no, restructure the section before continuing.

---

## BLUF — Bottom Line Up Front

US military communication standard, adopted into business comms because it respects readers'
time.

**Rule**: the first sentence of every section / paragraph / email / report tells the reader
the conclusion. Then the supporting reasoning. Never the other way around.

### Examples

**Bad (lede buried at the end):**

> "Over the past two weeks the team has been exploring authentication patterns. We considered
> JWT vs opaque tokens, weighed the security and operational tradeoffs, consulted with the
> platform team, and reviewed analogous decisions in our codebase. After discussion, we landed
> on JWT for cohesion with the existing stack. **This is now shipped and the frontend can
> start integrating.**"

**Good (BLUF):**

> **"Session creation is shipped — frontend can begin login integration."** We chose JWT over
> opaque tokens for cohesion with the existing auth stack; full rationale recorded as decision
> D1.

The second version respects the reader's time. The first one buries the actionable thing in
the last sentence.

### When BLUF is hard

If you can't write the BLUF version, it's usually because:

1. **You don't actually know the conclusion.** Step back; what's the takeaway? If there isn't
   one, the section may not belong.
2. **The conclusion sounds bad and you're softening it.** Don't. Honest amber/red wins trust.
3. **There are multiple conclusions.** Split into multiple sections.

---

## SCQA — Situation, Complication, Question, Answer

Barbara Minto's framework for the *opening* of any communication. Useful for the exec summary
specifically.

- **Situation**: where we are; what the reader already knows.
- **Complication**: what changed; what's new; what's the tension.
- **Question**: what the reader is now asking (implicit or explicit).
- **Answer**: the BLUF answer to that question.

### Example for a sprint update

- **Situation**: "We've been building the session API to support frontend login flows."
- **Complication**: "Two weeks ago we discovered a regulatory requirement for audit logs."
- **Question**: "Can we still ship by EOQ?"
- **Answer**: "Yes — audit log work is 75% done, on track for EOQ. One open decision (Q1) is
  the only risk to that date."

The exec summary's job is to *complete the SCQA*. By the end of the summary, the reader knows
where they are, what changed, what they should be wondering, and what the answer is.

---

## MECE — Mutually Exclusive, Collectively Exhaustive

McKinsey's grouping discipline. Two requirements:

- **ME**: no item appears in two groups
- **CE**: every relevant item appears in some group

### Why it matters for status reports

If "fix audit log bug" appears in both "shipped" and "in progress," the reader doesn't trust
the picture. If you list 3 risks but the reader knows of 2 more, they assume you're missing
others too.

### Application

For each list section:
- **ME check**: any item duplicated across sections? Pick one section, remove from the other.
- **CE check**: in this section's category, is the list complete? If not, either complete it
  or say "top 3 of N — see appendix for the rest."

The CE side is what most reports get wrong. They list "highlights" without saying what was
filtered out. The reader doesn't know if they're seeing 30% of the picture or 100%.

---

## The Five Cs

The qualitative bar for executive communication. Every sentence in the report should pass:

| C            | Question                                              | Failure mode                          |
| ------------ | ----------------------------------------------------- | ------------------------------------- |
| **Clear**    | Could a stakeholder outside the team understand this? | Jargon, undefined acronyms, code refs |
| **Concise**  | Is every word doing work?                             | Wordy, padded, hedged                 |
| **Concrete** | Could you point at the specific thing this refers to? | Vague ("we improved performance")     |
| **Compelling** | Does it answer "why should I care?"                 | List of activities with no narrative  |
| **Credible** | Would a skeptical reader trust this?                  | Overconfidence; no evidence; spin     |

The most-violated C in dev status reports is **Concrete**. "We made progress on the API" is
not concrete. "Session creation endpoint is live; tested with 3 user flows" is concrete.

---

## Miller's 7 ± 2

Human working memory holds 7 ± 2 items at once. A list of 12 items isn't read; it's skimmed.

**Application rules:**

- Exec summary: 3-5 bullets, never more.
- Headline metrics: 4-6 KPIs.
- Each list section ("shipped," "in progress," "risks"): 3-7 items. If you genuinely have
  more, group them into themes.
- Risks: if you have >7, that itself is the headline — surface "we are tracking 12 risks; top
  5 here, full list in appendix."

When you find yourself wanting to list more than 7, ask: **is there a parent category that
groups some of these?** Usually yes.

---

## RAG status — be honest

The Red / Amber / Green status indicator is a contract with your readers. Misusing it costs
trust.

### What each means

- **🟢 Green** — on track. No specific risks needing attention this period. Standard cadence
  applies.
- **🟡 Amber** — risks or decisions are outstanding that *could* affect outcomes. Attention
  warranted; possible action needed.
- **🔴 Red** — off-track, blocked, or in crisis. Escalation required now. Plan needs to
  change.

### The default-to-green trap

Most dev status reports are green by default. This is usually a lie. Real projects accumulate
risks, decisions, ambiguities every week — most of them are amber by an honest read.

**Heuristic**: if you have *any* blocker, *any* outstanding decision that affects ship date,
or *any* significant unknown, you're amber at minimum. Going green requires *all* of those to
be absent.

### The "watermelon" project

Green outside, red inside. Looks fine in reports, blows up at the deadline. Avoid by:

- Honest amber when there's any real risk
- Surfacing the specific risk (not "we're watching some risks")
- Naming who can resolve it and by when

A project that goes amber for 4 weeks and then green is healthier than one that's green
forever and then red on launch day.

---

## The "So what?" test

For every datapoint, every chart, every bullet — ask "so what?"

If you can answer it, write the answer next to the datapoint. **That's the report.**

If you can't, the datapoint doesn't belong.

### Examples

| Datapoint                                | So what?                                                                  |
| ---------------------------------------- | ------------------------------------------------------------------------- |
| "47 commits this week"                   | Activity normal for the sprint; no surge, no stall                        |
| "Compliance jumped from 50% → 75%"       | Major milestone unlocked; on track for EOQ ship                           |
| "R4 blocked on Q1"                       | Launch date at risk; decision needed from <user> by Friday                |
| "Test coverage steady at 78%"            | No regression; no investment either — propose +5% by EOM if it matters    |
| "PR throughput up 25%"                   | Team accelerating; matches expected curve after recent onboarding         |

A status report whose entire value is "look at all these numbers" isn't a status report —
it's a dashboard. Reports add **interpretation**.

---

## Common executive comms mistakes

The patterns to recognize and avoid:

### 1. The activity report

A list of what the team *did* (commits, meetings, PRs) with no interpretation of what it
*means*. Reads like a timesheet. Add the "what it means" column or cut it.

### 2. The jargon wall

"Refactored the action registry to support generic dispatch via discriminated union types,
unblocking the CoAgent provider for streaming token-level updates."

A non-engineer reads this and tunes out. Top of report should be jargon-free; jargon belongs
in drill-downs only.

### 3. The hedge

"Things are mostly going well, generally on track, though there are some areas we're keeping
an eye on, and a few items that may need attention soon."

What does any of that mean? Nothing. Be specific or be silent.

### 4. The "no risks" report

If there are genuinely zero risks, this isn't a real project. The "Risks" section should have
*something* — even "low: dependency on team X delivery; mitigated by parallel work." Otherwise
you look unprepared.

### 5. The activity-without-outcome

"Shipped 8 PRs this week." OK — what did they accomplish? "Shipped 8 PRs delivering 3
features: session create, session expiry, token refresh." Now we know.

### 6. The unprioritized list

Listing 5 risks without ordering or severity means the reader has to figure out which to care
about. You did the work — sort by impact.

### 7. The reader-as-judge framing

Writing as if to defend the team. "Despite challenges with X, we managed to ship Y." Drop the
"despite" and "managed to" — they signal anxiety. Just state what happened.

### 8. The action-less report

Every report should imply or state an action — even if it's "no action needed, continue
current plan." A report with no next step is incomplete.

### 9. The version-2 surprise

The report says everything is green. Two weeks later, the project is red. Going forward, the
reader doesn't trust green from this source again. **Honest amber along the way protects the
report's credibility forever after.**

### 10. The treadmill report

Same report every week with minor wording changes — "still working on X, still tracking Y."
Readers stop reading. If a section hasn't changed substantively, say "no change since [date]"
and move on; spend the words on what *did* change.

---

## Putting it together

A great status report:

1. Tells the reader the answer in the first paragraph (BLUF).
2. Lets them stop reading whenever their attention runs out and still be informed (Pyramid).
3. Has 3-7 items per section (7 ± 2) grouped MECE.
4. Translates every datapoint into business impact (So what?).
5. Uses honest RAG status with specific evidence.
6. Passes the Five Cs at every sentence.
7. Implies a next action.

These principles get applied automatically when the templates and structure in this skill
are followed. This file exists for when the *prose* itself needs tightening.
