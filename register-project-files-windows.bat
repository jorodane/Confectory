@echo off
setlocal DisableDelayedExpansion
set "confectory_entry_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_entry_dotnet=%CONFECTORY_DOTNET%"
if not exist "%~dp0.confectory" mkdir "%~dp0.confectory"
"%confectory_entry_dotnet%" "%~dp0targets\desktop-entry\bin\Release\net8.0\Confectory.DesktopEntry.dll" registration-file "%~dp0.confectory\Confectory.cproj.reg" --repository "%~dp0."
exit /b %errorlevel%
