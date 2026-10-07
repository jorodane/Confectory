@echo off
setlocal DisableDelayedExpansion
call "%~dp0verify-desktop-entry-windows.bat" >nul
if not errorlevel 1 exit /b 0

if not exist "%~dp0targets\desktop-entry\Confectory.DesktopEntry.csproj" goto source_missing
echo [Confectory] Installed desktop entry outputs are missing.
echo [Confectory] Building this trusted checkout in Release. The requested pack will not be built or run.
call "%~dp0build-windows.bat"
set "confectory_entry_build_exit=%errorlevel%"
if not "%confectory_entry_build_exit%"=="0" goto failed
call "%~dp0verify-desktop-entry-windows.bat"
exit /b %errorlevel%
:failed
echo [Confectory] Installation build failed with exit code %confectory_entry_build_exit%.
echo [Confectory] Check the diagnostics above and the existing .NET 10 SDK selected by global.json.
echo [Confectory] Retry build-windows.bat from this checkout. No tools or file associations were installed.
exit /b %confectory_entry_build_exit%
:source_missing
echo [Confectory] Desktop entry source is missing. Update the complete integration/checkpoint-18-native-ui checkout.
echo [Confectory] No requested pack was built or run.
exit /b 3
