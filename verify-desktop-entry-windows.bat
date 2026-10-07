@echo off
setlocal DisableDelayedExpansion
rem Read-only verification of the default solution Release/net10.0 installation.
for %%F in (
 "%~dp0targets\desktop-entry\bin\Release\net10.0\Confectory.DesktopEntry"
 "%~dp0src\Confectory.Cli\bin\Release\net10.0\Confectory.Cli"
 "%~dp0targets\dotnet\bin\Release\net10.0\Confectory.Build.DotNet"
 "%~dp0targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring"
 "%~dp0targets\project-execution-host\bin\Release\net10.0\Confectory.ProjectExecutionHost"
) do (
 for %%E in (dll deps.json runtimeconfig.json) do if not exist "%%~F.%%E" (
  echo [Confectory] Missing installed output: "%%~F.%%E"
  exit /b 3
 )
 rem The independent compiler tool has no Core assembly reference.
 if /i not "%%~nxF"=="Confectory.Build.DotNet" if not exist "%%~dpFConfectory.Core.dll" (
  echo [Confectory] Missing installed output: "%%~dpFConfectory.Core.dll"
  exit /b 3
 )
)
for %%F in (Microsoft.CodeAnalysis.dll Microsoft.CodeAnalysis.CSharp.dll) do if not exist "%~dp0targets\element-authoring\bin\Release\net10.0\%%F" (
 echo [Confectory] Missing authoring dependency: "%~dp0targets\element-authoring\bin\Release\net10.0\%%F"
 exit /b 3
)
exit /b 0
