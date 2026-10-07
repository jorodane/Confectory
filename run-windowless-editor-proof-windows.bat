@echo off
setlocal DisableDelayedExpansion
set "CONFECTORY_WINDOWLESS_EDIT=1"
call "%~dp0run-windowless-browser-proof-windows.bat" %*
exit /b %errorlevel%
