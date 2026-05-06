#Requires -Version 7.0
# Run this once to commit and push v4.0.0 to GitHub
Set-Location $PSScriptRoot
git add -A
git commit -m "v4.0.0: Expand to 20 intents, add slash command routing, discover_commands()"
git push
Write-Host ""
Write-Host "Done! Then re-install the updated detector:" -ForegroundColor Green
Write-Host "  .\install.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then regenerate your project CLAUDE.md:" -ForegroundColor Green
Write-Host "  python ~/.claude/adaptive-skills/detector.py --force" -ForegroundColor Cyan
