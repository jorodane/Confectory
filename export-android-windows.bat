@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0export-android-windows.ps1" %*
exit /b %errorlevel%
