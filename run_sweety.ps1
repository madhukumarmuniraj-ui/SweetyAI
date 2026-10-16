Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "          Starting SweetyAI Ecosystem...           " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$env:PYTHONIOENCODING = "utf-8"

Write-Host "Launching SweetyAI Backend, Vite Server, and Electron Desktop..." -ForegroundColor Green
npm run desktop
