@echo off
echo ========================================================
echo  Deploying Merge Kingdom Version 2.5 to GitHub
echo  Target: https://github.com/shubhamsavarn/Merge_Kingdom.git
echo ========================================================

:: Stage any modified files
git add .

:: Configure remote origin
git remote remove origin 2>nul
git remote add origin https://github.com/shubhamsavarn/Merge_Kingdom.git

:: Ensure branch name is main
git branch -M main

:: Commit changes
git commit -m "feat(architecture): complete Version 2.5 dual-currency system, live-ops backend, client SDK, and verification suite"

:: Push to GitHub
echo Pushing to GitHub (main branch)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Code successfully pushed to https://github.com/shubhamsavarn/Merge_Kingdom.git
) else (
    echo.
    echo [NOTE] If git push prompted for authentication, ensure you are logged into GitHub via Git Credential Manager or Personal Access Token.
)

pause

