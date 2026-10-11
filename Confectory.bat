@echo off
setlocal DisableDelayedExpansion
rem Normal entry opens actual EditorHome directly; a file argument opens that project.
set "CONFECTORY_LAUNCH_PROJECT="
if not "%~1"=="" set "CONFECTORY_LAUNCH_PROJECT=%~f1"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0scripts\windows\launcher.ps1" -Action editor
set "confectory_launch_exit=%errorlevel%"
if "%confectory_launch_exit%"=="0" exit /b 0
echo Confectory launcher failed. See diagnostics above and .confectory\launcher-logs.
if not "%CONFECTORY_NO_PAUSE%"=="1" pause
exit /b %confectory_launch_exit%
