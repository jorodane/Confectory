@echo off
setlocal DisableDelayedExpansion
rem One user entry. A file argument is context only: the menu still requires a choice.
set "CONFECTORY_LAUNCH_PROJECT="
if not "%~1"=="" set "CONFECTORY_LAUNCH_PROJECT=%~f1"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0scripts\windows\launcher.ps1"
set "confectory_menu_exit=%errorlevel%"
if "%confectory_menu_exit%"=="0" exit /b 0
echo Confectory launcher failed. See diagnostics above and .confectory\launcher-logs.
if not "%CONFECTORY_NO_PAUSE%"=="1" pause
exit /b %confectory_menu_exit%
