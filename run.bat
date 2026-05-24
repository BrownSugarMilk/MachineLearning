@echo off
REM 一键运行完整实验（Windows）
cd /d "%~dp0"

if exist my_venv\Scripts\activate.bat (
    call my_venv\Scripts\activate.bat
)

python run.py
if errorlevel 1 exit /b 1
