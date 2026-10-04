@echo off
cd /d "%~dp0"
echo Wattsense development simulator
echo Open http://127.0.0.1:8765 in your browser. Press Ctrl+C to stop.
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m wattsense.server --mode simulated
) else (
  python -m wattsense.server --mode simulated
)
pause

