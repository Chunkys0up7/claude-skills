# Data sources — what to pull and how

The skill's value depends on real data — not invented progress or vibes-based status. This
file is the deep guide to each source, the commands to use, and how to parse the output.

---

## Source 1 — `SPEC-COMPLIANCE.md` (the spec-guard tracker)

**If this file exists in the repo, it's the primary source.** It already has structured data:
requirements, statuses, evidence, decisions, questions.

### Where it lives

By default, `<repo-root>/SPEC-COMPLIANCE.md`. May also be:
- `docs/specs/<feature>-compliance.md` (per-feature)
- `.specs/progress.md`

### What to extract

From the tracker:
- **Requirements table** → spec items (ID, requirement, spec ref, status, evidence)
- **Acceptance criteria detail** → completion percentages for in-progress items
- **Out-of-spec changes** → "out-of-spec work this period" callout
- **Open questions** → Section 8 of the report
- **Decisions log** → Section 7 of the report
- **Change log** → period boundaries; what's new this report

### Status mapping

| Tracker status | Report category                |
| -------------- | ------------------------------ |
| 🟦 Verified    | Shipped (Section 4)            |
| ✅ Done        | Shipped, with "test gap" note  |
| 🟡 In progress | In progress (Section 5)        |
| ❌ Blocked    | Blocked (Section 6)            |
| ⬜ Not started | Next period plan (Section 10) |
| ➖ Deferred   | Mention in scope notes; appendix |

### Reading approach

```bash
# Just cat the file — it's structured markdown
cat SPEC-COMPLIANCE.md
```

When parsing, focus on the tables (they're the structured data). The Decisions log and Open
Questions sections are also tables. The narrative sections are useful context but the tables
are where the report content comes from.

---

## Source 2 — git log

The activity log. What was committed, by whom, what files changed.

### The "since" boundary

The report period needs an explicit start date. Options in order of preference:

1. **Since the last report's timestamp.** Read `docs/reports/latest.md`'s frontmatter
   `period_to:` value.
2. **Since a named tag** (release boundary). `git log --since="<tag>"`.
3. **Last 7 days** (default if no previous report). `git log --since="7 days ago"`.
4. **User-specified date** ("since 2026-05-15").

### Commands

```bash
# All commits in the period with short stats
git log --since="<from-date>" --until="<to-date>" \
  --pretty=format:'%h|%ad|%an|%s' --date=short --shortstat --no-merges

# Just the summary stats
git log --since="<from>" --until="<to>" --no-merges --shortstat | \
  tail -n 3   # last 3 lines have "N files changed, M insertions, K deletions"

# Commits per day (for the chart)
git log --since="<from>" --until="<to>" --no-merges \
  --pretty=format:'%ad' --date=short | sort | uniq -c

# Author breakdown
git log --since="<from>" --until="<to>" --no-merges \
  --pretty=format:'%an' | sort | uniq -c | sort -rn

# File hotspots (most-changed files this period)
git log --since="<from>" --until="<to>" --no-merges --name-only \
  --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -10
```

### Parsing approach

The `%h|%ad|%an|%s` format gives easy-to-parse pipe-delimited commits. Filter / group as
needed.

**Look for spec IDs in commit messages**: `R1`, `R3`, `Q2`, `D1`, `X1`. If commit messages
follow the `spec-guard` convention (`feat(R1): ...`), this directly maps commits to spec
items.

### Don't dump every commit

Most commits are not worth listing in the main report. Keep them in the appendix. The main
report uses git data to:
- Compute headline metrics (commits this period, lines changed)
- Identify file hotspots (signal for the in-progress / shipped narrative)
- Cross-reference commit messages with spec IDs

---

## Source 3 — `gh` CLI (GitHub PRs and issues)

If the project uses GitHub and `gh` is authenticated, this is rich structured data.

### PRs merged this period

```bash
# In bash:
gh pr list --state merged --limit 50 \
  --search "merged:>=<from-date> merged:<=<to-date>" \
  --json number,title,author,mergedAt,labels,body
```

### PRs in flight

```bash
gh pr list --state open --limit 50 \
  --json number,title,author,createdAt,labels,isDraft,reviewDecision
```

### Issues closed this period

```bash
gh issue list --state closed --limit 50 \
  --search "closed:>=<from-date> closed:<=<to-date>" \
  --json number,title,labels,closedAt
```

### Open blocker issues

```bash
gh issue list --state open --label blocker \
  --json number,title,labels,createdAt,body
```

### Parsing approach

`gh` outputs JSON with `--json`. Easy to consume directly.

**Key fields:**
- PR title and body — often contain feature descriptions, ready to lift for "what shipped"
- PR labels — `bug`, `feature`, `infra`, `breaking-change`, etc. — useful for grouping
- Issue labels — same
- Author/assignee — for team breakdown

### When `gh` isn't available

The skill still works without `gh`. Fall back to:
- Reading `CHANGELOG.md` (often more useful than PR titles anyway)
- Inferring features from commit messages (if they follow conventional commits)
- Asking the user to summarize what shipped

---

## Source 4 — `CHANGELOG.md`

If the project maintains one, it's a curated source — better than raw commits because it's
already been triaged.

### Conventions to detect

- **Keep a Changelog** format: `## [Unreleased]`, `### Added`, `### Changed`, `### Fixed`,
  `### Removed`.
- **Conventional Commits + auto-generated**: usually has version headers and commit categories.
- **Custom format**: read it as narrative.

### Use

If a `CHANGELOG.md` exists and has been updated this period, **lift the entries directly into
the "What shipped" section**, then add the "why it matters" interpretation.

```bash
# Find the section for the current report period
grep -A 100 "## \[Unreleased\]" CHANGELOG.md
# or for the latest release
grep -A 100 "^## \[" CHANGELOG.md | head -100
```

---

## Source 5 — Previous report

`docs/reports/latest.md` — the previous report's content.

### Why read it

- **Period boundary** — the `period_to:` field in the frontmatter sets the start of this
  report's period.
- **Continuity** — the previous "Next period plan" becomes this report's accountability
  check.
- **Trend baseline** — compare metrics to last period.
- **Decision history** — anything still open carries forward.

### Parsing

The MD format has YAML frontmatter. Parse with PyYAML or just grep the lines. Key fields:

```yaml
---
period_to: 2026-05-14
spec_compliance: 50
items_done: 6
items_blocked: 2
overall_status: yellow
---
```

This report's frontmatter compares against these values for trend indicators.

---

## Source 6 — CI / test status

Where available, pull current test pass rate and (optionally) coverage.

### Common sources

- **GitHub Actions**: `gh run list --limit 1 --json status,conclusion` for the latest run
- **`coverage.xml` / `lcov.info` / `coverage.json`** in repo if coverage is committed
- **`pytest --tb=no -q` exit code + summary** for a quick local run (if the user authorizes)

### What to extract

- Pass rate: passing / total
- Number of tests (for trend — growth is usually good)
- Coverage % (if reported)

### When unavailable

Skip the metric or note "test status not configured in this run."

---

## Source 7 — Custom project files

Some projects have other sources of truth:

- **Linear / Jira exports** — if the user has them locally as JSON or CSV
- **Notion / Confluence** — usually not directly accessible; ask the user to paste
- **Engineering metrics dashboards** — usually not directly accessible

For these, fall back to asking the user: "Anything from Linear/Jira/Notion I should
incorporate?"

---

## The gather order

When the skill runs, gather sources in this order (parallel where independent):

```
PARALLEL:
  1. cat SPEC-COMPLIANCE.md (if exists)
  2. read docs/reports/latest.md (if exists) for period boundary + baseline
  3. git log + git stats commands
  4. gh pr/issue commands (if gh available)
  5. CHANGELOG.md (if exists)
  6. CI status (if available)

THEN:
  7. Determine the period using previous report's period_to, or default
  8. Aggregate everything into the report data structure
```

### The optional convenience script

`scripts/gather_data.py` runs the common commands and outputs a single JSON blob. Use it for
fast repeat reports. It expects to be run from the repo root:

```bash
python <path-to-skill>/scripts/gather_data.py --since="<from-date>" > /tmp/report-data.json
```

Output structure roughly matches the `reportData` object the HTML template expects.

When the script isn't available (or for one-off reports), running the commands inline is
fine.

---

## When data is sparse

For a new project / first report, you might have only:
- A spec file (no tracker yet)
- A handful of commits

That's OK. The first report:
- Establishes the tracker (run `spec-guard` in retrospective audit mode first if not already
  done)
- Sets the period baseline ("first report — period from project start")
- Uses what data exists; explicitly notes what's missing

The skill works on whatever data is available — it doesn't require all sources to be present.

---

## Privacy / safety considerations

- **Never include private data** in the report (passwords, tokens, customer PII)
- **Be careful with author names** in external-facing reports — use roles ("the team," "ops")
  unless the audience expects names
- **Sanitize commit messages** if they contain anything sensitive
- **Don't expose internal-only labels** in customer-facing reports
- **Check the report before sending** for anything that shouldn't go to that audience

The skill outputs to local files; nothing is sent anywhere automatically. But what gets pasted
into Slack / email / a board deck is on the user — encourage a quick read-through before
sharing externally.
