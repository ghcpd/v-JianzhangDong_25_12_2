@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

if exist .venv\Scripts\python.exe (
  set PY=.venv\Scripts\python.exe
) else (
  rem Fallback to py launcher
  set PY=py
)

%PY% auto_test\auto_test.py --both

endlocal
