# claude-skills

Personal collection of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills, version-controlled so they sync across machines and sessions.

A "skill" is a folder under `~/.claude/skills/<skill-name>/` containing at minimum a `SKILL.md`. Claude Code loads them automatically and surfaces them via the Skill tool. This repo holds the source of truth; each skill directory is symlinked into `~/.claude/skills/` on every machine.

## Layout

```
claude-skills/
├── README.md
├── install.ps1          # Windows: symlinks every top-level dir into ~/.claude/skills
├── install.sh           # macOS/Linux: same, with ln -s
└── <skill-name>/
    ├── SKILL.md         # required — the skill's entry point
    └── ...              # supporting files, templates, scripts
```

## Skills

- **clean-code-guard** — Preventative cross-language code-quality guardrail. Catches "vibe coding" pathologies (sprawl, god objects, magic values, deep nesting, missing types, dead code, premature abstraction, etc.) before they ship. Fires on code-writing, refactoring, and design tasks across TypeScript, JavaScript, Python, Go, Rust, Java, and C#.
- **debug-guard** — Systematic debugging discipline. Prevents whack-a-mole fixing and the 3-hour spiral on a 20-minute bug. Enforces reproduce-before-fix, hypothesis-with-evidence, one-change-at-a-time, root-cause-not-symptom, and a circle-breaker after 3 failed attempts. Fires on broken code, stack traces, error messages, flaky tests, performance regressions. Deep playbook for UI / browser / network / proxy / CORS / cookies / dev proxies (Next.js, Vite, webpack) / reverse proxies (nginx, traefik) / corporate MITM certs / WebSocket / SSE / caching / CSP.
- **spec-guard** — Enforces spec-driven discipline for projects with existing specs (PRDs, RFCs, design docs, ADRs, acceptance criteria, API contracts). Two modes: **forward implementation** (building from spec — three rules: every change traces to a spec item, a compliance tracker is maintained as a real artifact, every non-trivial change gets an integration plan BEFORE code) and **retrospective audit** (reconciling existing code against a spec — nine-step playbook with spec→code and code→spec passes, evidence-gathering, test coverage and drift checks, prioritized findings report). Pairs with the broader `anthropic-skills:spec-driven-dev` process framework.
- **manager-update** — Generates business-consumable progress reports for managers, execs, stakeholders, and the board, pulling from the spec-guard tracker, git log, gh CLI, and the previous report. Two outputs in one run: a self-contained interactive HTML report (charts, collapsible drill-downs, print-ready) and a RAG-ready Markdown report (YAML frontmatter, stable headings, tech + business impact woven together). Enforces best-in-class exec-comms principles (Minto Pyramid, BLUF, SCQA, MECE, the Five Cs, Miller's 7±2, RAG status honesty) plus the "what it means" translation discipline on every datapoint. Outputs to `docs/reports/<date>-progress.{html,md}` with `latest.{html,md}` pointers. Target: under 5 minutes from request to delivered report.
- **copilotkit-setup** — Scaffold a CopilotKit (Next.js + FastAPI) in-app AI copilot, or debug install/runtime errors with `@copilotkit/*` packages.

## Install on a new machine

```powershell
git clone https://github.com/Chunkys0up7/claude-skills.git
cd claude-skills
./install.ps1
```

```bash
git clone https://github.com/Chunkys0up7/claude-skills.git
cd claude-skills
./install.sh
```

The install script creates a symlink at `~/.claude/skills/<skill-name>` for every top-level directory in this repo. Edits to the repo are reflected live — no copying step.

> **Windows note:** symlinks require Developer Mode enabled (Settings → System → For developers → Developer Mode) or an elevated shell. The script falls back to a directory junction (`mklink /J`) if symlink creation is denied — junctions work the same for Claude Code's purposes.

## Adding a new skill

1. Create `claude-skills/<skill-name>/SKILL.md` with the standard frontmatter:
   ```markdown
   ---
   name: <skill-name>
   description: When to trigger this skill (be specific — this is what Claude matches against).
   ---
   ```
2. Run `./install.ps1` again to create the symlink.
3. Commit and push.

## Removing a skill

```powershell
Remove-Item "$env:USERPROFILE\.claude\skills\<skill-name>"  # removes only the symlink
```

Then delete the directory from this repo and push.
