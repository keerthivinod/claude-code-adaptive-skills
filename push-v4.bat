@echo off
cd /d "%~dp0"
git add -A
git commit -m "v4.0.0: Expand to 20 intents, add slash command routing, discover_commands()"
git push
echo.
echo Done! Now run install.ps1 to update your local detector.
pause
