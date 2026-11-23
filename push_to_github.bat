@echo off
setlocal enabledelayedexpansion
title Push Zomato Analysis Project to GitHub

echo =====================================================================
echo           Zomato Restaurant Analysis - GitHub Push Helper
echo =====================================================================
echo.

cd /d "%~dp0"

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git from https://git-scm.com/ and try again.
    pause
    exit /b 1
)

echo [1/4] Checking Git repository initialization...
if not exist ".git" (
    echo Initializing fresh Git repository...
    git init
    git branch -M main
) else (
    echo Git repository already initialized.
)

echo.
echo [2/4] Staging and committing project files...
git add .
git commit -m "Initial commit: Complete Zomato restaurant market analysis project"

echo.
echo [3/4] GitHub Remote Configuration:
git remote get-url origin >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%u in ('git remote get-url origin') do set CURRENT_REMOTE=%%u
    echo Current remote origin is: !CURRENT_REMOTE!
    set /p CHANGE_REMOTE="Do you want to update this remote URL? (y/N): "
    if /i "!CHANGE_REMOTE!"=="y" (
        set /p REPO_URL="Enter your new GitHub repository URL: "
        if not "!REPO_URL!"=="" (
            git remote set-url origin !REPO_URL!
        )
    )
) else (
    echo Please create a new empty repository on GitHub (https://github.com/new).
    set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/zomato-analysis.git): "
    if not "!REPO_URL!"=="" (
        git remote add origin !REPO_URL!
    ) else (
        echo No repository URL provided. Skipping push.
        pause
        exit /b 0
    )
)

echo.
echo [4/4] Pushing to GitHub (main branch)...
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =====================================================================
    echo   [SUCCESS] Project pushed successfully to your GitHub repository!
    echo =====================================================================
) else (
    echo.
    echo [NOTE] If the push was rejected because the remote repo has files (like a default README/license),
    echo you can force push or pull first:
    echo   git pull origin main --allow-unrelated-histories
    echo   git push -u origin main
)

echo.
pause
