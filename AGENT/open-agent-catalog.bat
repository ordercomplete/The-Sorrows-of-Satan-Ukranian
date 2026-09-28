@echo off
python "%~dp0scripts\generate-agent-catalog.py"
if errorlevel 1 (
	echo Catalog generation failed.
	pause
	exit /b 1
)
start "" "%~dp0agent-catalog.html"
