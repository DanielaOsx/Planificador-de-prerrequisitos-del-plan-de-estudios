@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install -q pytest networkx
  py -m pytest -v
) else (
  python -m pip install -q pytest networkx
  python -m pytest -v
)
pause
