# Symlinks every top-level skill directory in this repo into ~/.claude/skills/.
# Re-run safely after adding new skills.

$ErrorActionPreference = "Stop"

$repoRoot   = $PSScriptRoot
$skillsRoot = Join-Path $env:USERPROFILE ".claude\skills"

if (-not (Test-Path $skillsRoot)) {
    New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
    Write-Host "Created $skillsRoot"
}

$skills = Get-ChildItem -Path $repoRoot -Directory |
    Where-Object { $_.Name -notmatch '^\.' -and $_.Name -ne 'node_modules' }

foreach ($skill in $skills) {
    $target = $skill.FullName
    $link   = Join-Path $skillsRoot $skill.Name

    if (Test-Path $link) {
        $item = Get-Item $link -Force
        if ($item.LinkType -in @("SymbolicLink", "Junction")) {
            $existingTarget = $item.Target | Select-Object -First 1
            if ($existingTarget -eq $target) {
                Write-Host "OK   $($skill.Name) -> already linked"
                continue
            }
            Write-Host "REPL $($skill.Name) (was -> $existingTarget)"
            Remove-Item $link -Force
        } else {
            Write-Warning "SKIP $($skill.Name): $link exists and is not a symlink/junction. Move or remove it manually, then re-run."
            continue
        }
    }

    try {
        New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null
        Write-Host "LINK $($skill.Name) (symlink)"
    } catch {
        # Symlinks need Developer Mode or admin. Junctions don't — fall back.
        cmd /c mklink /J "`"$link`"" "`"$target`"" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "LINK $($skill.Name) (junction)"
        } else {
            Write-Error "Failed to create symlink or junction for $($skill.Name)"
        }
    }
}

Write-Host ""
Write-Host "Done. Restart any running Claude Code session to pick up new skills."
