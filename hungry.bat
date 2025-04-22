@echo off
color 0A
title "HUNGRY CRAWLER"
mode con: cols=120 lines=40

echo [92m
echo  HUNGRY CRAWLER
echo  ==============
echo [0m

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m[ERROR] Python is not installed or not in PATH.[0m
    echo [97mPlease install Python from https://www.python.org/downloads/[0m
    echo.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo [91mVirtual environment not found.[0m
    echo [97mPlease run setup.bat first to install dependencies.[0m
    echo.
    pause
    exit /b 1
)

echo [92mStarting Hungry Crawler...[0m

:: Activate virtual environment and run the script
call venv\Scripts\activate.bat
python crawler_scraper.py %*

:: The script handles its own exit, no need for deactivation here
:: as it will never reach this point due to os._exit(0)
