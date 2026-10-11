@echo off
setlocal DisableDelayedExpansion
rem Explicit developer tools only. Root Confectory.bat starts the editor directly.
set "CONFECTORY_LAUNCH_PROJECT="
if not "%~1"=="" set "CONFECTORY_LAUNCH_PROJECT=%~f1"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0launcher.ps1" -Action menu
set "confectory_tools_exit=%errorlevel%"
if not "%confectory_tools_exit%"=="0" if not "%CONFECTORY_NO_PAUSE%"=="1" pause
exit /b %confectory_tools_exit%
