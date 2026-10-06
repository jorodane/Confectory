@echo off
setlocal DisableDelayedExpansion
rem Double-click entry: ordinary CMD and existing dotnet only. No PowerShell.
set "confectory_home_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_home_dotnet=%CONFECTORY_DOTNET%"
pushd "%~dp0"
if errorlevel 1 goto directory_failed
set "confectory_home_pushed=1"
set "CONFECTORY_EDITOR_REPO=%CD%"
set "confectory_home_log=%CD%\.confectory\home-launch.log"
if not exist ".confectory" mkdir ".confectory"
if not exist ".confectory" goto log_failed
> "%confectory_home_log%" echo Confectory Entry/Home launch: %date% %time%
if errorlevel 1 goto log_failed
>> "%confectory_home_log%" echo Repository: "%CD%"
>> "%confectory_home_log%" echo Selected .NET host: "%confectory_home_dotnet%"
echo [Confectory 1/3] Checking the existing SDK selected by global.json.
call "%confectory_home_dotnet%" --version >> "%confectory_home_log%" 2>&1
set "confectory_home_exit=%errorlevel%"
if not "%confectory_home_exit%"=="0" goto sdk_failed
echo [Confectory 1/3] Building solution and editor tool hosts.
echo Build and runtime output: "%confectory_home_log%"
call "%~dp0build-windows.bat" >> "%confectory_home_log%" 2>&1
set "confectory_home_exit=%errorlevel%"
if not "%confectory_home_exit%"=="0" goto report_failed
echo [Confectory 2/3] Building Windows Entry/Home ProjectPack, then launching it.
echo First uncached pack compilation can take a few minutes.
echo The Editor will open when compilation finishes. Keep this window open.
call "%confectory_home_dotnet%" "src\Confectory.Cli\bin\Release\net8.0\Confectory.Cli.dll" run "examples\editor-home\project.cpack" windows >> "%confectory_home_log%" 2>&1
set "confectory_home_exit=%errorlevel%"
if not "%confectory_home_exit%"=="0" goto report_failed
popd
exit /b 0
:directory_failed
set "confectory_home_exit=%errorlevel%"
echo Cannot enter the repository folder containing this launcher.
goto pause_failed
:log_failed
set "confectory_home_exit=1"
echo Cannot write the launch log in this checkout's .confectory folder.
echo Use a complete checkout in a folder where you have write permission.
goto pause_failed
:sdk_failed
echo The existing .NET host could not select the required .NET 8 SDK.
echo global.json remains unchanged; a runtime alone is insufficient.
echo Check the diagnostics below and CONFECTORY_DOTNET if set.
echo CONFECTORY_DOTNET should be the full path to an existing SDK8 dotnet.exe.
:report_failed
echo.
if exist "%confectory_home_log%" type "%confectory_home_log%"
echo.
echo Confectory Entry/Home launch failed with exit code %confectory_home_exit%.
echo Diagnostics retained at: "%confectory_home_log%"
:pause_failed
if not "%CONFECTORY_NO_PAUSE%"=="1" pause
if defined confectory_home_pushed popd
exit /b %confectory_home_exit%
