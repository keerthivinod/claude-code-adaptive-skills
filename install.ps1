#Requires -Version 7.0
<#
.SYNOPSIS
    Installs claude-code-adaptive-skills on Windows (PowerShell 7+).

.DESCRIPTION
    - Copies detector.py to ~/.claude/adaptive-skills/
    - Patches your PowerShell profile with a directory-change hook
    - Runs a smoke test to verify Python can execute it

.PARAMETER Uninstall
    Remove the hook from your profile and delete ~/.claude/adaptive-skills/

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Uninstall
#>

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# ── Config ────────────────────────────────────────────────────────────────────
$CLAUDE_DIR     = Join-Path $HOME ".claude"
$INSTALL_DIR    = Join-Path $CLAUDE_DIR "adaptive-skills"
$DETECTOR_SRC   = Join-Path $PSScriptRoot "detector.py"
$DETECTOR_DEST  = Join-Path $INSTALL_DIR "detector.py"
$PROFILE_PATH   = $PROFILE.CurrentUserAllHosts   # profile loaded in all PS hosts

$HOOK_START = "# >>> claude-code-adaptive-skills >>>"
$HOOK_END   = "# <<< claude-code-adaptive-skills <<<"
$HOOK_BODY  = @"
$HOOK_START
function Invoke-AdaptiveSkills {
    `$detector = Join-Path `$HOME ".claude\adaptive-skills\detector.py"
    if (Test-Path `$detector) {
        try {
            python `$detector `$PWD 2>`$null
        } catch {}
    }
}
function global:Set-Location {
    Microsoft.PowerShell.Management\Set-Location @args
    Invoke-AdaptiveSkills
}
$HOOK_END
"@

# ── Uninstall ─────────────────────────────────────────────────────────────────
if ($Uninstall) {
    Write-Host ""
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Uninstalling claude-code-adaptive-skills   " -ForegroundColor Cyan
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""

    # Remove install dir
    if (Test-Path $INSTALL_DIR) {
        Remove-Item -Recurse -Force $INSTALL_DIR
        Write-Host "  ✓ Removed $INSTALL_DIR" -ForegroundColor Green
    } else {
        Write-Host "  (install dir not found — skipping)" -ForegroundColor Gray
    }

    # Strip hook from profile
    if (Test-Path $PROFILE_PATH) {
        $content = Get-Content $PROFILE_PATH -Raw
        if ($content.Contains($HOOK_START)) {
            $pattern = "(?ms)\r?\n?$([regex]::Escape($HOOK_START)).*?$([regex]::Escape($HOOK_END))\r?\n?"
            $newContent = [regex]::Replace($content, $pattern, "")
            Set-Content $PROFILE_PATH $newContent -NoNewline
            Write-Host "  ✓ Hook removed from profile: $PROFILE_PATH" -ForegroundColor Green
        } else {
            Write-Host "  (hook not found in profile — skipping)" -ForegroundColor Gray
        }
    }

    Write-Host ""
    Write-Host "  Done. Restart PowerShell to apply changes." -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# ── Install ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Installing claude-code-adaptive-skills     " -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    Write-Host "      $pyVer" -ForegroundColor Gray
} catch {
    Write-Host "      ERROR: Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Copy detector.py
Write-Host "[2/4] Copying detector.py to $INSTALL_DIR ..." -ForegroundColor Yellow
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Force $INSTALL_DIR | Out-Null
}
if (-not (Test-Path $DETECTOR_SRC)) {
    Write-Host "      ERROR: detector.py not found at $DETECTOR_SRC" -ForegroundColor Red
    exit 1
}
Copy-Item $DETECTOR_SRC $DETECTOR_DEST -Force
Write-Host "      ✓ Copied to $DETECTOR_DEST" -ForegroundColor Green

# Step 3: Patch PowerShell profile
Write-Host "[3/4] Patching PowerShell profile..." -ForegroundColor Yellow
Write-Host "      Profile: $PROFILE_PATH" -ForegroundColor Gray

# Ensure profile exists
if (-not (Test-Path $PROFILE_PATH)) {
    New-Item -ItemType File -Force $PROFILE_PATH | Out-Null
    Write-Host "      Created profile file" -ForegroundColor Gray
}

$currentContent = Get-Content $PROFILE_PATH -Raw
if ($null -eq $currentContent) { $currentContent = "" }

if ($currentContent.Contains($HOOK_START)) {
    Write-Host "      Hook already present — skipping." -ForegroundColor Gray
} else {
    Add-Content $PROFILE_PATH "`n$HOOK_BODY"
    Write-Host "      ✓ Hook added to profile" -ForegroundColor Green
}

# Step 4: Smoke test
Write-Host "[4/4] Running smoke test..." -ForegroundColor Yellow
try {
    $output = python $DETECTOR_DEST $PSScriptRoot --dry-run 2>&1
    Write-Host "      ✓ Smoke test passed" -ForegroundColor Green
    if ($output) {
        Write-Host "      Output: $output" -ForegroundColor Gray
    }
} catch {
    Write-Host "      WARNING: Smoke test had an issue: $_" -ForegroundColor Yellow
    Write-Host "      The hook is installed but verify Python can run detector.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✓ Installation complete!                   " -ForegroundColor Green
Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "  1. Close and reopen PowerShell (or run: . `$PROFILE)" -ForegroundColor Gray
Write-Host "  2. cd into any project folder" -ForegroundColor Gray
Write-Host "  3. A tailored CLAUDE.md will be generated automatically" -ForegroundColor Gray
Write-Host ""
Write-Host "  To uninstall:  .\install.ps1 -Uninstall" -ForegroundColor Gray
Write-Host ""
