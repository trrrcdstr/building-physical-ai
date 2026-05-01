@echo off
cd /d "%~dp0"
echo ======================================
echo Building Physical AI - 一键启动
echo ======================================
echo.
echo Starting services...
python start_all.py
pause
