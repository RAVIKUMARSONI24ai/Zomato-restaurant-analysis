@echo off
title Zomato Restaurant Analytics Dashboard
echo ========================================================
echo       Launching Zomato Restaurant Analytics Dashboard
echo ========================================================
echo.
cd /d "%~dp0"
python -m streamlit run dashboard\app.py
pause
