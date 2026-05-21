#!/usr/bin/env python3
"""
gather_data.py — optional convenience: pull data from a repo's various sources
(SPEC-COMPLIANCE.md, git log, gh CLI, CHANGELOG.md, previous report) and emit
a single JSON blob the manager-update skill can use.

Usage:
    python gather_data.py --since=2026-05-14 --to=2026-05-21
    python gather_data.py --days=7
    python gather_data.py --since-tag=v1.2.0

The script is intentionally permissive — sources that don't exist are skipped
without error. Sources that fail are reported in the output `warnings` field.

Output: JSON to stdout. Pipe or redirect to a file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command, capture output. Never raise."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout, p.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return -1, "", str(e)


def resolve_repo_root() -> Path:
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"])
    return Path(out.strip()) if code == 0 else Path.cwd()


def gather_git_log(repo: Path, since: str, until: str) -> dict:
    code, out, err = run(
        [
            "git", "log",
            f"--since={since}", f"--until={until}",
            "--no-merges",
            "--pretty=format:%h|%ad|%an|%s",
            "--date=short",
        ],
        cwd=repo,
    )
    if code != 0:
        return {"commits": [], "_warning": f"git log failed: {err.strip()}"}

    commits = []
    for line in out.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({"hash": parts[0], "date": parts[1], "author": parts[2], "subject": parts[3]})
    return {"commits": commits, "count": len(commits)}


def gather_git_shortstat(repo: Path, since: str, until: str) -> dict:
    code, out, _ = run(
        ["git", "log", f"--since={since}", f"--until={until}", "--no-merges", "--shortstat"],
        cwd=repo,
    )
    if code != 0:
        return {}
    # parse lines like " 12 files changed, 234 insertions(+), 56 deletions(-)"
    files = inserts = deletes = 0
    for line in out.splitlines():
        m = re.search(r"(\d+) files? changed", line)
        if m: files += int(m.group(1))
        m = re.search(r"(\d+) insertions?\(\+\)", line)
        if m: inserts += int(m.group(1))
        m = re.search(r"(\d+) deletions?\(-\)", line)
        if m: deletes += int(m.group(1))
    return {"files_changed": files, "insertions": inserts, "deletions": deletes}


def gather_commits_per_day(repo: Path, since: str, until: str) -> list[dict]:
    code, out, _ = run(
        ["git", "log", f"--since={since}", f"--until={until}", "--no-merges",
         "--pretty=format:%ad", "--date=short"],
        cwd=repo,
    )
    if code != 0:
        return []
    counts: dict[str, int] = {}
    for line in out.splitlines():
        counts[line] = counts.get(line, 0) + 1
    return sorted([{"date": d, "count": c} for d, c in counts.items()], key=lambda x: x["date"])


def gather_file_hotspots(repo: Path, since: str, until: str, top_n: int = 10) -> list[dict]:
    code, out, _ = run(
        ["git", "log", f"--since={since}", f"--until={until}", "--no-merges",
         "--name-only", "--pretty=format:"],
        cwd=repo,
    )
    if code != 0:
        return []
    counts: dict[str, int] = {}
    for f in out.splitlines():
        f = f.strip()
        if f:
            counts[f] = counts.get(f, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: -x[1])[:top_n]
    return [{"file": f, "changes": c} for f, c in ranked]


def gather_authors(repo: Path, since: str, until: str) -> list[dict]:
    code, out, _ = run(
        ["git", "log", f"--since={since}", f"--until={until}", "--no-merges", "--pretty=format:%an"],
        cwd=repo,
    )
    if code != 0:
        return []
    counts: dict[str, int] = {}
    for a in out.splitlines():
        if a.strip():
            counts[a] = counts.get(a, 0) + 1
    return sorted([{"author": a, "commits": c} for a, c in counts.items()], key=lambda x: -x["commits"])


def gather_gh_prs_merged(repo: Path, since: str, until: str) -> list[dict]:
    if run(["gh", "--version"])[0] != 0:
        return []
    code, out, _ = run(
        ["gh", "pr", "list", "--state", "merged", "--limit", "50",
         "--search", f"merged:>={since} merged:<={until}",
         "--json", "number,title,author,mergedAt,labels"],
        cwd=repo,
    )
    if code != 0:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def gather_gh_issues_closed(repo: Path, since: str, until: str) -> list[dict]:
    if run(["gh", "--version"])[0] != 0:
        return []
    code, out, _ = run(
        ["gh", "issue", "list", "--state", "closed", "--limit", "50",
         "--search", f"closed:>={since} closed:<={until}",
         "--json", "number,title,labels,closedAt"],
        cwd=repo,
    )
    if code != 0:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def gather_gh_open_blockers(repo: Path) -> list[dict]:
    if run(["gh", "--version"])[0] != 0:
        return []
    code, out, _ = run(
        ["gh", "issue", "list", "--state", "open", "--label", "blocker",
         "--json", "number,title,labels,createdAt"],
        cwd=repo,
    )
    if code != 0:
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def read_file_if_exists(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return None


def read_previous_report_meta(repo: Path) -> dict:
    """Read frontmatter of docs/reports/latest.md if present."""
    p = repo / "docs" / "reports" / "latest.md"
    text = read_file_if_exists(p)
    if not text or not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
    except ValueError:
        return {}
    meta = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather data for a manager-update report.")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD). Default: from previous report or 7 days ago.")
    parser.add_argument("--to", help="End date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--days", type=int, help="Period length in days (used if --since not given).")
    parser.add_argument("--since-tag", help="Use a git tag as the start boundary.")
    parser.add_argument("--repo", help="Repo root (default: auto-detect).")
    args = parser.parse_args()

    repo = Path(args.repo).resolve() if args.repo else resolve_repo_root()
    if not repo.exists():
        print(f"Repo not found: {repo}", file=sys.stderr)
        return 1

    # Resolve date range
    today = date.today().isoformat()
    until = args.to or today

    if args.since:
        since = args.since
    elif args.since_tag:
        # Use tag date
        code, out, _ = run(["git", "log", "-1", "--format=%ad", "--date=short", args.since_tag], cwd=repo)
        since = out.strip() if code == 0 else (date.today() - timedelta(days=7)).isoformat()
    else:
        prev = read_previous_report_meta(repo)
        if prev.get("period_to"):
            since = prev["period_to"]
        else:
            days = args.days or 7
            since = (date.today() - timedelta(days=days)).isoformat()

    data: dict = {
        "meta": {
            "repo": str(repo),
            "period_from": since,
            "period_to": until,
            "generated": datetime.utcnow().isoformat() + "Z",
        },
        "warnings": [],
    }

    # Spec compliance tracker
    spec_path = repo / "SPEC-COMPLIANCE.md"
    if spec_path.exists():
        data["spec_compliance_raw"] = spec_path.read_text(encoding="utf-8")
    else:
        data["warnings"].append("SPEC-COMPLIANCE.md not found at repo root.")

    # CHANGELOG
    cl_path = repo / "CHANGELOG.md"
    if cl_path.exists():
        data["changelog_raw"] = cl_path.read_text(encoding="utf-8")

    # Previous report
    prev = read_previous_report_meta(repo)
    if prev:
        data["previous_report_meta"] = prev

    # Git activity
    data["git"] = {
        "log": gather_git_log(repo, since, until),
        "shortstat": gather_git_shortstat(repo, since, until),
        "commits_per_day": gather_commits_per_day(repo, since, until),
        "file_hotspots": gather_file_hotspots(repo, since, until),
        "authors": gather_authors(repo, since, until),
    }

    # GitHub via gh CLI (optional)
    data["github"] = {
        "prs_merged": gather_gh_prs_merged(repo, since, until),
        "issues_closed": gather_gh_issues_closed(repo, since, until),
        "open_blockers": gather_gh_open_blockers(repo),
    }
    if not data["github"]["prs_merged"]:
        data["warnings"].append("gh CLI unavailable or no PRs found in period.")

    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
