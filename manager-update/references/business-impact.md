# Business impact — the "what it means" discipline

The translation layer that turns a tech change into a business outcome. This is the *entire
value* of a manager update over a raw git log.

The mental move: stop describing **what the code does** and start describing **what changed
for the business**.

---

## The translation discipline

For every shipped item, every in-progress item, every decision, every risk — answer the
question: **"so what?"**

A status report is read in 30 seconds by busy people. They need to know: does this change
what I do / care / spend / risk?

### Bad → Good examples

| Bad (tech-only)                                                   | Good (with business impact)                                                              |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| "Refactored auth into a separate module."                          | "Auth refactor unblocks the security review — required for SOC2 audit (Sept target)."     |
| "Added Redis cache."                                               | "Redis cache cuts product page load from 800ms → 200ms; expected to recover cart abandonment to ~3% from current 6%." |
| "Migrated to new logging library."                                 | "New logging gives ops actionable alerts on payment failures — reduces detection time from hours to minutes." |
| "Wrote 12 new tests."                                              | "New test coverage on checkout: regressions caught before production. Reduces hotfix rate."     |
| "Implemented JWT token refresh."                                   | "Users now stay logged in for 30 days instead of 24 hours — expected to reduce login friction; matches competitor experience." |
| "Bumped Node from 18 to 20."                                       | "Node 20 brings 15% faster cold-start on Lambda — small reliability win; also unblocks dependency upgrades stuck on 18." |
| "Fixed a bug in audit logging."                                    | "Audit logging now correctly records admin actions. Closes compliance gap from last quarter's audit." |

The pattern in every "good" example: **the tech change is one clause; the business meaning is
the rest of the sentence.**

---

## The categories of business impact

Every meaningful tech change maps to one or more of these categories. When stuck on "so what,"
pick the category and write to it.

### 1. Revenue

Does this directly enable or accelerate revenue?

- New feature customers pay for
- Conversion-rate improvement (checkout, signup, upgrade)
- Reduced churn (retention, win-back)
- Upsell / cross-sell capability

**Phrasing**: "Enables / accelerates X for customer segment Y." Avoid round-number revenue
claims unless they're real and modeled.

### 2. Cost

Does this reduce operational cost?

- Lower infra cost (compute, storage, bandwidth)
- Lower support cost (self-service, fewer tickets)
- Lower vendor cost (replaced vendor, reduced usage)
- Lower team cost (automation, reduced manual work)

**Phrasing**: "Reduces X cost by Y" if you have the number; otherwise "saves N hours/week of
manual work on Z."

### 3. Risk

Does this reduce probability or impact of a bad outcome?

- Security vulnerability closed
- Compliance gap closed (GDPR, SOC2, HIPAA, PCI, regional regs)
- Data integrity protected (backups, audit, replication)
- Production stability (test coverage, error handling, alerting)
- Vendor concentration reduced

**Phrasing**: "Closes / mitigates X risk." If there's a regulatory or audit deadline, name
it.

### 4. Customer experience

Does this make the product better for customers in a way they'll notice?

- Speed (latency, load time)
- Reliability (uptime, error rates seen by users)
- Usability (fewer steps, clearer errors, better defaults)
- Capability (new things customers can do)

**Phrasing**: "Customers can now X" or "X feels Y% faster" with specific numbers if you have
them.

### 5. Time-to-market

Does this make the team / product faster?

- Unblocks future work
- Removes a dependency
- Enables parallel development
- Reduces a critical-path bottleneck

**Phrasing**: "Unblocks X for Y team / next quarter / future feature."

### 6. Team velocity / quality

Does this make the team itself more effective?

- Build / test / deploy speed
- Easier onboarding
- Less toil (manual ops work)
- Better tooling
- Reduced cognitive load (cleaner code, better architecture)

**Phrasing**: Be careful here — "we cleaned up the code" is the lowest-credibility business
impact. Tie it to a concrete future delivery: "Refactor reduces onboarding time for the
incoming hires next month."

---

## Per-item translation templates

When writing the "Why it matters" line for a shipped or in-progress item, pick the template
that matches:

### For a customer-facing feature

> Customers can now [verb in plain English]. This [enables / unblocks / replaces / improves]
> [specific business outcome].

Example: "Customers can now stay logged in for 30 days. This reduces login friction and
matches competitor experience — expected to lift weekly active sessions by ~10%."

### For an internal capability

> [Team / system] can now [verb]. This [enables / accelerates / reduces risk of / replaces]
> [specific future work or risk].

Example: "The ops team can now alert on payment failures in real time. This reduces detection
time from hours to minutes and unblocks the 99.9% uptime commitment for enterprise tier."

### For a refactor / cleanup

> [System / module] now [shape / capability]. This [unblocks / enables / reduces friction
> for] [specific upcoming work].

Example: "The auth module is now isolated with a defined interface. This unblocks the
security review (required for SOC2 audit, September target) and makes the upcoming SSO
integration straightforward."

### For a dependency / infra change

> [Dependency / infra] is now [state]. This [enables / closes / reduces] [concrete outcome].

Example: "Node runtime is now on 20.x. This brings 15% faster cold-start on Lambda and
unblocks 4 dependency upgrades that were stuck on Node 18."

### For a bug fix

> [User-visible behavior] is fixed. This [restores / unblocks / reduces / closes] [specific
> outcome].

Example: "Mobile users no longer see duplicate confirmation emails on signup. Closes a top-3
support ticket category (~40 tickets/week)."

### For test / quality work

> [Surface] now has [coverage / monitoring / alerting]. This [reduces risk of / catches /
> protects against] [specific failure mode].

Example: "Checkout flow now has integration test coverage for all 6 payment methods. Reduces
risk of the regression we saw in March (3-hour outage, ~$80k impact)."

---

## Common bad translations to avoid

These are the patterns that destroy report credibility.

### 1. The vague handwave

> "This improves customer experience."

How? By what? Measured how? Replace with specifics or cut.

### 2. The overpromise

> "This will double our conversion rate."

Unless you have a model that supports the claim, you're going to be wrong publicly. Use ranges
or "expected to lift" with reasoning.

### 3. The unfalsifiable claim

> "This makes the codebase more maintainable."

By what measure? For how long? Tie to a specific outcome ("supports the 3 features planned
for Q3") or cut.

### 4. The future-tense escape

> "This will save us time later."

When? On what? Who? Be specific or cut. "Later" is a black hole.

### 5. The proxy metric

> "This adds 200 lines of code." (or removes them, or whatever)

LOC isn't a business outcome. Don't dress activity up as impact.

### 6. The dependency cascade

> "This enables future work that will enable other future work that will enable a feature."

Each layer of "enables" weakens the claim. Pick the closest concrete outcome.

### 7. The team-flattery report

> "The team did an amazing job shipping this."

Drop. Report-level praise feels like cheerleading; let the work speak.

### 8. The defensive framing

> "Despite challenges with X, we managed to ship Y."

The "despite" and "managed to" signal anxiety. Just state what happened.

---

## When you can't translate

If a tech change genuinely has no business impact, **don't pad the report with it.** Cut it.
Or move it to the appendix as "infra activity."

Common examples that often *don't* belong in the main report:

- Pure refactors with no upcoming work they unblock
- Renames / formatting
- Internal documentation updates
- Test fixture cleanup
- Dev tooling improvements with no time-saved measurement

If pressed to include them, group as "Maintenance and infra (no customer impact this period)"
and one line is enough.

---

## When the impact is hard to quantify

Many real changes have impact that's hard to put a number on. That's fine — don't fake the
number; use **directional language**:

- "Materially reduces" / "noticeably improves" / "small but compounding"
- "Sets up" / "unblocks" / "closes the gap on"
- "Risk-down" / "speed-up" / "cost-down" without false precision

The honesty is the value. A directional claim that's right beats a numeric claim that's wrong.

---

## Audience tuning

The same change has different framings for different audiences. The skill defaults to
"manager + exec" but allows the user to specify the audience. Adjust accordingly:

| Audience               | Emphasize                                                   | De-emphasize                          |
| ---------------------- | ----------------------------------------------------------- | ------------------------------------- |
| Board / C-level        | Revenue, risk, strategic enabling; competitive context      | Tech detail, team specifics            |
| Exec (VP)              | Time-to-market, delivery confidence, cross-team dependencies | Implementation detail                  |
| Manager                | Status against plan, team health, decision needs           | Strategic positioning                  |
| Engineering lead       | Technical debt, architecture progress, team velocity       | Marketing framing                      |
| Customer (release notes) | New capability, fixed bugs, performance                    | Internal infra, refactors              |
| Investor / external    | Milestones hit, KPIs, competitive position                 | Internal team dynamics                 |

Use the audience parameter to weight which "category of impact" to lead with. Same data,
different lede.

---

## The credibility compound

The single biggest determinant of whether reports get read over time is **the reader's history
of trusting what they said.** Every report either adds to or subtracts from that trust.

- Honest amber when the project is amber → +trust
- Numbers that turn out to be right → +trust
- Items called "shipped" that are really shipped → +trust
- Vague claims that don't survive scrutiny → -trust
- Overpromises that don't deliver → -trust (lots)
- Reports that hide problems until they explode → -trust (massive)

The discipline isn't about looking good in any one report. It's about being the source the
reader believes by week 12. Honest, specific, and direct beats polished, vague, and
optimistic every time.
