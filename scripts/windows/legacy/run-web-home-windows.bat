@echo off
setlocal DisableDelayedExpansion
echo [Legacy demo] Import-only web prototype, not the current EditorHome or embedded HTML editor.
set "confectory_browser_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_browser_dotnet=%CONFECTORY_DOTNET%"
pushd "%~dp0..\..\..\"
if errorlevel 1 exit /b 1
"%confectory_browser_dotnet%" --version >nul 2>nul
if errorlevel 1 goto failed
call "%~dp0..\..\..\scripts\windows\internal\build-windows.bat"
if errorlevel 1 goto failed
"%confectory_browser_dotnet%" build "targets\web\Confectory.Build.Web.csproj" -c Release
if errorlevel 1 goto failed
set "CONFECTORY_EDITOR_REPO=%CD%"
echo The legacy local host prints a localhost URL. It is not an embedded editor.
"%confectory_browser_dotnet%" "src\Confectory.Cli\bin\Release\net10.0\Confectory.Cli.dll" run "examples\editor-home-web\project.cproj" web
set "confectory_browser_exit=%errorlevel%"
popd
exit /b %confectory_browser_exit%
:failed
set "confectory_browser_exit=%errorlevel%"
echo Legacy browser demo failed. Read the SDK/build diagnostics above.
popd
exit /b %confectory_browser_exit%
