@echo off
setlocal DisableDelayedExpansion
echo [Legacy demo] This is not the current EditorHome. Use Confectory.bat for the editor.
rem Checkpoint 3 uses the same ordinary engine ProjectPack with its authoring slice enabled.
set "CONFECTORY_ELEMENT_UI=1"
if not defined CONFECTORY_ELEMENT_AUTHORING_HOST set "CONFECTORY_ELEMENT_AUTHORING_HOST=%~dp0..\..\..\targets\element-authoring\bin\Release\net10.0\Confectory.ElementAuthoring.dll"
call "%~dp0..\..\..\scripts\windows\legacy\run-engine-windows.bat"
exit /b %errorlevel%
