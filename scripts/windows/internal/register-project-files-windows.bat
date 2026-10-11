@echo off
setlocal DisableDelayedExpansion
call "%~dp0..\..\..\scripts\windows\internal\ensure-desktop-entry-windows.bat"
if errorlevel 1 exit /b %errorlevel%
set "confectory_entry_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_entry_dotnet=%CONFECTORY_DOTNET%"
if not exist "%~dp0..\..\..\.confectory" mkdir "%~dp0..\..\..\.confectory"
if not exist "%~dp0..\..\..\.confectory" exit /b 3
"%confectory_entry_dotnet%" "%~dp0..\..\..\targets\desktop-entry\bin\Release\net10.0\Confectory.DesktopEntry.dll" registration-file "%~dp0..\..\..\.confectory\Confectory.cproj.reg" --repository "%~dp0..\..\..\."
exit /b %errorlevel%
