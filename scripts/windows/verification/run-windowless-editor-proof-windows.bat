@echo off
setlocal DisableDelayedExpansion
set "CONFECTORY_WINDOWLESS_EDIT=1"
call "%~dp0..\..\..\scripts\windows\verification\run-windowless-browser-proof-windows.bat" %*
exit /b %errorlevel%
