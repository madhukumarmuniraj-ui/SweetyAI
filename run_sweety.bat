@echo off
TITLE SweetyAI - One-Click Desktop Companion Launcher
COLOR 0B

echo ====================================================================
echo                 Starting SweetyAI Vision Studio...
echo ====================================================================

cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

:: Step 1: Kill any dangling previous instances of electron
echo [1/3] Clearing lingering ports and processes...
taskkill /F /IM electron.exe 2>nul

:: Step 2: Build latest frontend changes
echo [2/3] Building latest frontend UI assets...
call npm run build

:: Step 3: Launch Full-Stack Ecosystem
echo [3/3] Launching Python Intelligence Engine & Electron Transparent UI...
echo ====================================================================
echo SweetyAI is online! Click the chick logo or mic icon to chat/talk.
echo ====================================================================

npm run desktop
