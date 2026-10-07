@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" (
 echo Usage: open-project-windows.bat "C:\folder\project.cproj"
 exit /b 2
)
call "%~dp0ensure-desktop-entry-windows.bat"
set "confectory_entry_exit=%errorlevel%"
if not "%confectory_entry_exit%"=="0" goto report_failed
set "confectory_entry_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_entry_dotnet=%CONFECTORY_DOTNET%"
"%confectory_entry_dotnet%" "%~dp0targets\desktop-entry\bin\Release\net8.0\Confectory.DesktopEntry.dll" open "%~1" --repository "%~dp0."
set "confectory_entry_exit=%errorlevel%"
:report_failed
if not "%confectory_entry_exit%"=="0" if not "%CONFECTORY_NO_PAUSE%"=="1" pause
exit /b %confectory_entry_exit%
