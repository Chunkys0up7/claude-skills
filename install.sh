#!/usr/bin/env bash
# Symlinks every top-level skill directory in this repo into ~/.claude/skills/.
# Re-run safely after adding new skills.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_root="${HOME}/.claude/skills"

mkdir -p "$skills_root"

shopt -s nullglob
for skill_dir in "$repo_root"/*/; do
    name="$(basename "$skill_dir")"
    # Skip hidden/build dirs
    case "$name" in
        .*|node_modules) continue ;;
    esac

    link="$skills_root/$name"
    target="${skill_dir%/}"

    if [[ -L "$link" ]]; then
        existing="$(readlink "$link")"
        if [[ "$existing" == "$target" ]]; then
            echo "OK   $name -> already linked"
            continue
        fi
        echo "REPL $name (was -> $existing)"
        rm "$link"
    elif [[ -e "$link" ]]; then
        echo "SKIP $name: $link exists and is not a symlink. Move or remove it manually, then re-run." >&2
        continue
    fi

    ln -s "$target" "$link"
    echo "LINK $name"
done

echo ""
echo "Done. Restart any running Claude Code session to pick up new skills."
