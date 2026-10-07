@echo off
setlocal
rem Checkpoint 3 uses the same ordinary engine ProjectPack with its authoring slice enabled.
set "CONFECTORY_ELEMENT_UI=1"
if not defined CONFECTORY_ELEMENT_AUTHORING_HOST set "CONFECTORY_ELEMENT_AUTHORING_HOST=%~dp0targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring.dll"
call "%~dp0run-engine-windows.bat"
exit /b %errorlevel%
