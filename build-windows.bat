@echo off
setlocal

rem Use the explicitly selected .NET host, or dotnet from PATH.
set "confectory_dotnet=dotnet"
if defined CONFECTORY_DOTNET set "confectory_dotnet=%CONFECTORY_DOTNET%"

pushd "%~dp0"
if errorlevel 1 exit /b 1

"%confectory_dotnet%" build "Confectory.sln" --configuration Release --nologo
set "confectory_exit=%errorlevel%"

popd
exit /b %confectory_exit%
