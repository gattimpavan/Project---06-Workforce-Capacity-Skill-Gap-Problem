@echo off
title Infosys Workforce Capacity & Skill Gap Intelligence Dashboard
echo =========================================================================
echo   INFOSYS WORKFORCE CAPACITY & SKILL GAP INTELLIGENCE SYSTEM
echo   Project - 06: Autonomous Business Operations
echo =========================================================================
echo.
echo Starting Flask web server on port 5006...
echo Dashboard will be live at: http://localhost:5006
echo Executive PDF Report available at: http://localhost:5006/api/download_report
echo.
cd /d "%~dp0"
"C:\Users\hp\AppData\Local\Programs\Orange\python.exe" app.py
pause

