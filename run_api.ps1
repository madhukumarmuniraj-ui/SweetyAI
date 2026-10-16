$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
& ".\.venv\Scripts\python.exe" (Join-Path $PSScriptRoot "server.py")
