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
