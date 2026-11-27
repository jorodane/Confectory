@echo off
setlocal DisableDelayedExpansion
rem A separate persistent test profile enables an actual cold reopen.
set "sample_source=%~dp0examples\performance-sample"
if not exist "%sample_source%\project.cpack" set "sample_source=%~dp0content\examples\performance-sample"
if not exist "%sample_source%\project.cpack" goto failed
if "%LOCALAPPDATA%"=="" goto failed
set "sample_root=%LOCALAPPDATA%\Confectory\PerformanceSample-v1"
if not exist "%sample_root%" (
    mkdir "%sample_root%"
    if errorlevel 1 goto failed
)
if not exist "%sample_root%\project" (
    xcopy "%sample_source%\*" "%sample_root%\project\" /E /I /Q >nul
    if errorlevel 1 goto failed
)
if not exist "%sample_root%\project\project.cpack" goto failed
set "CONFECTORY_HOME_STORAGE=%sample_root%\profile"
set "CONFECTORY_ENTRY_STORAGE=%sample_root%\entry"
set "CONFECTORY_MCP_DIRECTORY=%sample_root%\instances"
set "CONFECTORY_WEB_PROJECT="
set "CONFECTORY_BROWSER_PROJECT="
echo Open this disposable project through the editor's Open existing project button:
echo "%sample_root%\project\project.cpack"
call "%~dp0Confectory-performance.bat"
exit /b %errorlevel%
:failed
echo Could not prepare the isolated performance sample. Existing files are not overwritten.
pause
exit /b 1
