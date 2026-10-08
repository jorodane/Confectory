@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0export-android-windows.ps1" %*
set "confectory_export_exit=%errorlevel%"
if not "%confectory_export_exit%"=="0" echo Android export failed ^(exit %confectory_export_exit%^). Read the diagnostics above.
rem No arguments is the interactive picker/double-click entry. Explicit CLI arguments never pause.
if "%~1"=="" pause
exit /b %confectory_export_exit%
