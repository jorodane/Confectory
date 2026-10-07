@echo off
setlocal DisableDelayedExpansion
set "confectory_windowless_exit=2"
if "%CONFECTORY_WINDOWLESS_EDIT%"=="1" goto editable_banner
echo Confectory windowless browser proof - Windows x64, read-only
goto project_input
:editable_banner
echo Confectory EXPERIMENTAL native editing bridge - Windows x64
echo Real Windows native editing, IME, clipboard and DPI validation are pending.
:project_input
if not "%~1"=="" set "CONFECTORY_BROWSER_PROJECT=%~f1"
if defined CONFECTORY_BROWSER_PROJECT goto check_project
echo Enter the full path to an existing project.cpack.
echo Nothing is created or moved by this launcher.
set /p "CONFECTORY_BROWSER_PROJECT=Project path: "
:check_project
if not defined CONFECTORY_BROWSER_PROJECT goto missing_project
if not exist "%CONFECTORY_BROWSER_PROJECT%" goto missing_project
set "confectory_windowless_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_windowless_dotnet=%CONFECTORY_DOTNET%"
pushd "%~dp0"
if errorlevel 1 goto bad_directory
echo Building existing .NET 10 tools. Build output follows.
call "%~dp0build-windows.bat"
if errorlevel 1 goto failed
set "CONFECTORY_ELEMENT_AUTHORING_HOST=%CD%\targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring.dll"
echo Launching windowless browser for "%CONFECTORY_BROWSER_PROJECT%"
call "%confectory_windowless_dotnet%" "src\Confectory.Cli\bin\Release\net10.0\Confectory.Cli.dll" run "examples\windowless-browser-proof\project.cpack" windows
set "confectory_windowless_exit=%errorlevel%"
popd
goto finished
:failed
set "confectory_windowless_exit=1"
echo Build failed. See the compiler output above.
popd
goto finished
:bad_directory
set "confectory_windowless_exit=1"
echo Could not enter the repository directory.
goto finished
:missing_project
echo Project not found. Provide an existing project.cpack path without surrounding quotes.
echo Usage: run-windowless-browser-proof-windows.bat "C:\path\to\project.cpack"
:finished
echo Launcher exit code: %confectory_windowless_exit%
echo Default mode is read-only. Editable mode is an unverified host bridge experiment.
if not defined CONFECTORY_NO_PAUSE pause
exit /b %confectory_windowless_exit%
