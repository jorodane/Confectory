@echo off
setlocal DisableDelayedExpansion
if not "%~1"=="" set "CONFECTORY_BROWSER_PROJECT=%~f1"
if not defined CONFECTORY_BROWSER_PROJECT goto missing_project
if not exist "%CONFECTORY_BROWSER_PROJECT%" goto missing_project
set "confectory_windowless_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_windowless_dotnet=%CONFECTORY_DOTNET%"
pushd "%~dp0"
if errorlevel 1 exit /b 1
call "%~dp0build-windows.bat"
if errorlevel 1 goto failed
set "CONFECTORY_ELEMENT_AUTHORING_HOST=%CD%\targets\element-authoring\bin\Release\net8.0\Confectory.ElementAuthoring.dll"
call "%confectory_windowless_dotnet%" "src\Confectory.Cli\bin\Release\net8.0\Confectory.Cli.dll" run "examples\windowless-browser-proof\project.cpack" windows
set "confectory_windowless_exit=%errorlevel%"
popd
exit /b %confectory_windowless_exit%
:failed
popd
exit /b 1
:missing_project
echo Usage: run-windowless-browser-proof-windows.bat "C:\path\to\project.cpack"
echo Choose an existing project. No project is created or moved automatically.
exit /b 2
