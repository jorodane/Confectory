@echo off
setlocal DisableDelayedExpansion
set "confectory_browser_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_browser_dotnet=%CONFECTORY_DOTNET%"
cd /d "%~dp0"
"%confectory_browser_dotnet%" --version >nul 2>nul
if errorlevel 1 (
 echo .NET 8 SDK is required for the local browser host.
 exit /b 1
)
call build-windows.bat nopause
if errorlevel 1 exit /b 1
"%confectory_browser_dotnet%" build "targets\web\Confectory.Build.Web.csproj" -c Release
if errorlevel 1 exit /b 1
set "CONFECTORY_EDITOR_REPO=%~dp0"
echo The local host will print a http://127.0.0.1 URL. Open it in your browser.
echo This is a local .NET host, not an independent browser/WASM runtime.
"%confectory_browser_dotnet%" "src\Confectory.Cli\bin\Release\net8.0\Confectory.Cli.dll" run "examples\editor-home-web\project.cproj" web
exit /b %errorlevel%
