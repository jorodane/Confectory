@echo off
setlocal
rem Double-click or run from CMD. Build-only behavior remains in build-windows.bat.
set "confectory_launcher_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_launcher_dotnet=%CONFECTORY_DOTNET%"
pushd "%~dp0"
if errorlevel 1 goto failed
set "confectory_pushed=1"
echo [Confectory 1/3] Building solution with %confectory_launcher_dotnet%
call "%~dp0build-windows.bat"
set "confectory_exit=%errorlevel%"
if not "%confectory_exit%"=="0" goto report_failed
if not defined CONFECTORY_PROJECT_EXECUTION_HOST set "CONFECTORY_PROJECT_EXECUTION_HOST=%CD%\targets\project-execution-host\bin\Release\net8.0\Confectory.ProjectExecutionHost.dll"
if not defined CONFECTORY_PROJECT_ROOT set "CONFECTORY_PROJECT_ROOT=%CD%"
echo [Confectory 2/3] Building Windows engine ProjectPack, then launching it.
echo First uncached pack compilation can take a while; progress stages follow below.
call "%confectory_launcher_dotnet%" "src\Confectory.Cli\bin\Release\net8.0\Confectory.Cli.dll" run "examples\engine\project.cpack" windows
set "confectory_exit=%errorlevel%"
if not "%confectory_exit%"=="0" goto report_failed
popd
exit /b 0
:failed
set "confectory_exit=%errorlevel%"
:report_failed
echo.
echo Confectory engine launch failed with exit code %confectory_exit%.
echo Read the build or runtime diagnostics above.
if not "%CONFECTORY_NO_PAUSE%"=="1" pause
if defined confectory_pushed popd
exit /b %confectory_exit%
