---
name: manager-update
description: |
  Generates business-consumable progress reports for managers, executives, stakeholders,
  customers, and board members from real project data — the spec-guard compliance tracker,
  git activity, PR/issue state, CI/test status, and the CHANGELOG. Produces TWO outputs in
  one run: a self-contained interactive HTML report (exec-friendly, charts, collapsible
  drill-downs, print-ready) and a RAG-ready Markdown report (frontmatter, structured headings,
  tech + business impact woven together so a RAG can answer questions from either lens). Both
  land in `docs/reports/`.
  Fires whenever the user asks for a status update, progress report, manager update, exec
  readout, weekly/sprint summary, stakeholder update, release notes, project health snapshot,
  delivery report, or "where are we" / "what's shipped" / "what's the state of X" question.
  Triggers on phrases like: "manager update", "exec report", "progress report", "status
  report", "weekly update", "sprint summary", "release notes", "give me a readout", "where
  are we on X", "what's shipped this week", "report on the project", "build a progress
  dashboard", "executive summary", "what should I tell my manager", "stakeholder update",
  "delivery report", "project health", "we have a steering meeting", "I need to brief
  leadership", "summarize the work since <date>", "what's been done since <tag>", "build me a
  readout for <audience>".
  ENFORCES best-in-class executive communication: Barbara Minto's Pyramid Principle (headline
  → supporting points → detail), BLUF (Bottom Line Up Front), SCQA (Situation → Complication
  → Question → Answer), MECE (Mutually Exclusive, Collectively Exhaustive groupings), the
  "Five Cs" (Clear, Concise, Concrete, Compelling, Credible), the "So what?" test on every
  datapoint, Miller's 7±2 rule for chunking, and explicit RAG (Red/Amber/Green) status
  indicators. Every datapoint gets a "what it means" interpretation — the report is not a
  data dump.
  Designed to run OFTEN — low friction, smart defaults (last 7 days, since last report,
  since tag X), pulls data automatically from `SPEC-COMPLIANCE.md` + `git log` + `gh` CLI +
  `CHANGELOG.md`. Target: under 5 minutes from request to delivered report.
  Complements `spec-guard` (which produces the tracker this skill reads), `data:build-
  dashboard` (which is generic — this skill is opinionated for dev progress with the "what
  it means" layer baked in), and `marketing:performance-report` (which is for marketing
  metrics, not dev progress).
---

# manager-update

Turns project data into a business-readable narrative — fast, repeatable, and built so the
*messaging* (not the report-building) is where you spend your time.

The principle: **a report should be a 5-minute task, not a half-day project.** That only works
if (a) the data is gathered automatically, (b) the structure is fixed, and (c) the "what it
means" translation discipline is codified rather than improvised every time.

## Core principles

### 1. Pyramid first, detail last

**Barbara Minto's Pyramid Principle**: the headline at the top is a summary of everything below
it. The reader can stop at any level and still have the right understanding for *their* level
of interest.

- **Exec summary** → 3-5 sentences. A C-level should be able to read this and stop.
- **Headline metrics + status** → managers stop here.
- **What shipped / what's blocked / what's next** → team leads stop here.
- **Drill-downs** → engineers and curious readers go here.

This is what makes one report work for five different audiences without writing five reports.

### 2. BLUF — Bottom Line Up Front

The first sentence of every section answers: **what should the reader take away?** Then
supporting points. Never bury the lede.

Bad: "We've been working on session creation, which involved discussions about JWT vs opaque
tokens. We landed on JWT for cohesion with existing services. This is now shipped."

Good: "**Session creation is shipped** — frontend can begin login integration. (We chose JWT
over opaque tokens for cohesion; rationale recorded.)"

### 3. Every datapoint passes the "So what?" test

Every metric, every shipped item, every chart must answer "so what?" — the business
interpretation. If you can't articulate the *meaning*, the datapoint doesn't belong in the
report (or it needs more thought before it does).

| Datapoint                       | So what? (what it means)                                                  |
| ------------------------------- | ------------------------------------------------------------------------- |
| "47 commits this week"          | Activity level is steady; matches sprint plan; no surge or stall          |
| "Compliance jumped 40% → 75%"   | Major milestone unblocked; on track for end-of-quarter ship target        |
| "R4 blocked on Q1"              | Launch date at risk; decision needed today from <user>                    |

The "what it means" column is non-negotiable. It's the *entire value* of the report over a raw
data dump.

### 4. MECE groupings

When you list things in a section — **M**utually **E**xclusive (no overlap), **C**ollectively
**E**xhaustive (nothing missed). Otherwise readers don't trust the picture.

Don't have one item appear in both "shipped" and "in progress." Don't list 4 risks if there
are 7. If the section is incomplete, say so.

### 5. 7 ± 2 — chunking

Per Miller's law, working memory tops out around 7 ± 2 items. Sections with 12 bullets get
skimmed and forgotten. Group / merge / cut until each section has 3-7 items.

If you genuinely have 15 risks, that's a finding in itself — surface it and link to the
appendix.

### 6. Status — RAG honestly

🟢 **Green** — on track, no escalation needed
🟡 **Amber** — attention warranted; specific risks or decisions outstanding
🔴 **Red** — blocked / off-track; escalation needed now

**Don't be optimistic by default.** Amber-when-actually-amber is what builds trust over time.
A report that's been green every week for 8 weeks and then suddenly red is worse than honest
amber along the way.

---

## The standard structure

Ten sections, in this order. Skip sections that genuinely don't apply (and say so). See
[`references/content-structure.md`](./references/content-structure.md) for what goes in each.

1. **Executive summary** — 3-5 bullets, BLUF. C-level stops here.
2. **Headline metrics** — KPI cards with trend. Numeric snapshot.
3. **Overall status** — 🟢 / 🟡 / 🔴 with one-line justification.
4. **What shipped** — each item: *what* (plain English) + *why it matters* (business impact) +
   technical reference.
5. **In progress** — with % complete, expected ship, blocker-or-next.
6. **Blocked / decisions needed** — RED CALLOUT section. What's blocked, why, who decides, by
   when, impact of delay.
7. **Decisions made this period** — for the record (and the RAG). Brief rationale.
8. **Open questions** — outstanding ambiguities awaiting input.
9. **Risks** — with severity, owner, mitigation. Action-oriented.
10. **Next period plan** — top 3-5 things. What "done" looks like.

Plus an **appendix** with raw activity (commits, PRs, issues) for the curious.

---

## The workflow

### Step 1 — Determine scope

Ask (or infer):

- **Period**: last 7 days? since last report? since tag `v1.2.0`? Default: since the timestamp
  on `docs/reports/latest.md`, or last 7 days if no previous report exists.
- **Audience**: manager / exec / customer / board / mixed? Affects tone and drill-down depth.
  Default: "manager + exec" (most common).
- **Project scope**: whole repo, or one feature/epic? Default: whole repo.

If the user didn't specify, propose defaults and proceed. Don't make a long interview out of
this — they want the report, not a survey.

### Step 2 — Gather data

In parallel, pull from:

- **`SPEC-COMPLIANCE.md`** (if present) — the spec-guard tracker. Source of truth for
  requirement status, evidence, decisions, questions.
- **`git log --since="<period>" --pretty=format:'%h %ad %an %s' --shortstat`** — what was
  committed, by whom, files/lines changed.
- **`gh pr list --state merged --search "merged:>=<date>"`** (if `gh` available) — PRs landed.
- **`gh issue list --state closed --search "closed:>=<date>"`** — issues closed.
- **`gh pr list --state open`** — what's in flight.
- **`gh issue list --state open --label blocker`** — current blockers.
- **`CHANGELOG.md`** — if maintained.
- **CI status** — if a status JSON is exposed somewhere.
- **Previous report** — `docs/reports/latest.md` if it exists. Provides the comparison baseline.

There's an optional convenience script: `scripts/gather_data.py` — runs the common commands
and outputs a JSON blob. Use it for repeated reports; you don't have to.

See [`references/data-sources.md`](./references/data-sources.md) for the deep guide on each
source.

### Step 3 — Translate to business impact

For each shipped item and each in-progress item, write the "what it means" interpretation.
This is the discipline section that turns a tech log into an exec report.

The mental move: stop thinking "what did the code do" and start thinking "what changed for the
user / the business / the team / the risk profile."

See [`references/business-impact.md`](./references/business-impact.md) for the translation
patterns and the categories of impact (revenue, cost, risk, customer experience, time-to-
market, team velocity).

### Step 4 — Apply the structural discipline

Map every gathered datapoint into the 10 sections. Cut ruthlessly:

- Each section: 3-7 items max.
- Each item: one-line plain English plus one-line "what it means."
- Drop minor commits unless they roll up into a feature.
- Group related work into themes; don't list every PR as a separate item.

### Step 5 — Render

Generate both outputs:

- **HTML**: load `assets/report-template.html`. The template has a `const reportData = {...};`
  placeholder near the top. Write the data object in place; save as
  `docs/reports/<YYYY-MM-DD>-progress.html`. Update `docs/reports/latest.html` (a copy, not a
  symlink — most file viewers don't follow symlinks).
- **Markdown**: render the same data into `assets/report-template.md`. Save as
  `docs/reports/<YYYY-MM-DD>-progress.md`. Update `docs/reports/latest.md`.

### Step 6 — Deliver

Output to the conversation:

- One-line summary ("Report generated; status: 🟡 — see Blockers, R4 needs Q1 decision today")
- File paths of the two outputs
- A one-paragraph TL;DR the user can paste into Slack / email if they don't want to attach
  the file

---

## The HTML output

Self-contained single file:

- Inline CSS (no Tailwind CDN dep — fully portable)
- Chart.js via CDN (one external dep, ~80kb gzipped; falls back gracefully if offline)
- A `const reportData = { ... }` block at the top with all the data
- JavaScript that reads the data and populates the DOM
- Print-friendly stylesheet (some execs print)
- Mobile-responsive
- Interactivity: collapsible sections, filter chips, click-to-expand cards
- Accessible color palette with status colors (🟢 / 🟡 / 🔴 distinguishable for colorblind
  readers — also uses icons)

The template is at `assets/report-template.html`. Don't modify the template per-report —
write the data into the placeholder and save the result.

---

## The Markdown output (RAG-ready)

YAML frontmatter for metadata, structured headings for chunking, narrative paragraphs for
context. Same data as the HTML, but written for retrieval-augmented generation.

Key design choices for RAG-friendliness:

- **Frontmatter** — project, period, status, compliance %, audiences, key IDs. Lets the RAG
  filter and rank.
- **Stable section headings** — `## What shipped`, `## In progress`, etc. — same every
  report. RAG can answer "what was shipped in week 21" by chunking on these.
- **TL;DR section** — a paragraph of self-contained context that a RAG can grab as the
  "elevator pitch" for the whole report.
- **Each shipped/in-progress item has** the same structure (What / Why it matters / Tech /
  Evidence / Spec ref) so cross-report comparisons are clean.
- **Cross-references** to spec items (`R1`, `Q3`, etc.) and to previous reports
  (`docs/reports/<date>-progress.md`).
- **No images, no JS, no external deps.**

Template at `assets/report-template.md`.

---

## Output to the conversation

Keep the in-chat response short — the report is the artifact, not the chat. Default response:

```
**Report generated** — `docs/reports/2026-05-21-progress.html` + `.md` · 🟡 amber

TL;DR: 9/12 spec items complete (75%, +25% this week). One blocker: R4 (rate
limiting) needs decision on Q1 today to keep launch on track. Three features
shipped this period (session create, session expiry, refresh).

Outputs:
- HTML: docs/reports/2026-05-21-progress.html
- MD:   docs/reports/2026-05-21-progress.md
- Latest pointers updated.
```

If the user wants more, they open the report. If they want less, the TL;DR is the report.

---

## What this skill is NOT

- **Not a substitute for the spec-guard tracker.** It *reads* the tracker; the tracker is
  still the live, working document.
- **Not a marketing comms generator.** Different tone, different audience. Use
  `marketing:performance-report` for those.
- **Not a dashboard builder for live data.** The HTML is a point-in-time snapshot. For live
  data, use `data:build-dashboard`.
- **Not an excuse for inflation.** A report that overstates progress to look good destroys
  trust the moment reality catches up. The skill enforces honest RAG status; surface amber
  and red when warranted.

---

## See also

- [`references/exec-comms.md`](./references/exec-comms.md) — Barbara Minto's Pyramid
  Principle, BLUF, SCQA, MECE, the Five Cs, Miller's 7±2, RAG status discipline. The "why"
  behind the structure.
- [`references/content-structure.md`](./references/content-structure.md) — what goes in each
  of the 10 sections, how to phrase items, what to cut, what to keep.
- [`references/business-impact.md`](./references/business-impact.md) — the "what it means"
  discipline. Translation patterns from tech to business; categories of impact; common bad
  translations to avoid.
- [`references/data-sources.md`](./references/data-sources.md) — how to pull from
  SPEC-COMPLIANCE.md, git log, gh CLI, CHANGELOG, CI status, and previous reports. The
  commands and parsing logic.
- [`assets/report-template.html`](./assets/report-template.html) — the interactive HTML
  template. Single file, Chart.js via CDN, data-driven.
- [`assets/report-template.md`](./assets/report-template.md) — the RAG-ready Markdown
  template with YAML frontmatter.
- [`scripts/gather_data.py`](./scripts/gather_data.py) — optional convenience: gathers data
  from all sources and emits a JSON blob.
