@echo off
rem ============================================================
rem Vercel AI Gateway Supervisor - запуск супервізора чату
rem ============================================================
cd /d D:\GEN\Comfy-smart-lady-agent
powershell -NoProfile -ExecutionPolicy Bypass -File "AGENT\scripts\vercel-supervisor.ps1"
pause