@echo off
setlocal DisableDelayedExpansion
call "%~dp0Confectory.bat" --performance
set "confectory_result=%errorlevel%"
if exist "%LOCALAPPDATA%\Confectory\Performance" explorer.exe "%LOCALAPPDATA%\Confectory\Performance"
exit /b %confectory_result%
