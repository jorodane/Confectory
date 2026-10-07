@echo off
setlocal DisableDelayedExpansion

rem Use the explicitly selected .NET host, or dotnet from PATH.
set "confectory_build_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_build_dotnet=%CONFECTORY_DOTNET%"

pushd "%~dp0"
if errorlevel 1 exit /b 1

"%confectory_build_dotnet%" build "Confectory.sln" --configuration Release --nologo
set "confectory_exit=%errorlevel%"
if not "%confectory_exit%"=="0" goto finished

rem Build success must include the desktop entry and its required installed hosts.
call "%~dp0verify-desktop-entry-windows.bat"
set "confectory_exit=%errorlevel%"
if not "%confectory_exit%"=="0" echo [Confectory] Expected Release/net8.0 outputs are missing. Check the checkout version, solution project list and custom output/framework overrides.
:finished
popd
exit /b %confectory_exit%
