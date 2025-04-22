@echo off
color 0A
title "HUNGRY CRAWLER - SETUP"
mode con: cols=120 lines=40

echo [92m
echo  HUNGRY CRAWLER SETUP
echo  ====================
echo [0m

:: Check if Python is installed
echo [93mVerifying Python installation...[0m
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m[ERROR] Python is not installed or not in PATH.[0m
    echo [97mPlease install Python from https://www.python.org/downloads/[0m
    echo.
    pause
    exit /b 1
)
echo [92mPython detected![0m

:: Create virtual environment if it doesn't exist
echo [93mCreating virtual environment...[0m
if not exist venv (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [91m[ERROR] Failed to create virtual environment.[0m
        echo.
        pause
        exit /b 1
    )
    echo [92mVirtual environment created![0m
) else (
    echo [92mVirtual environment already exists![0m
)

:: Activate virtual environment
echo [93mActivating virtual environment...[0m
call venv\Scripts\activate.bat
echo [92mVirtual environment activated![0m

:: Install required packages
echo [93mInstalling required packages...[0m
pip install requests beautifulsoup4 rich pyfiglet markdown pathlib urllib3 certifi
echo [92mPackages installed![0m

:: Create necessary directories
echo [93mCreating system directories...[0m
for %%d in (Results Crawled Exports Logs) do (
    if not exist %%d (
        mkdir %%d
        echo [92mCreated %%d directory![0m
    ) else (
        echo [92m%%d directory already exists![0m
    )
)

:: Create settings file if it doesn't exist
echo [93mConfiguring system settings...[0m
if not exist settings.json (
    echo {> settings.json
    echo     "respect_robots_txt": true,>> settings.json
    echo     "crawl_delay": 2,>> settings.json
    echo     "max_pages": 100,>> settings.json
    echo     "timeout": 15,>> settings.json
    echo     "max_retries": 3,>> settings.json
    echo     "user_agent": "HungryCrawler/1.0",>> settings.json
    echo     "blacklist": [],>> settings.json
    echo     "whitelist": [],>> settings.json
    echo     "export_formats": ["json", "csv", "txt", "md"],>> settings.json
    echo     "use_proxies": false,>> settings.json
    echo     "proxies": [],>> settings.json
    echo     "rotate_user_agents": true,>> settings.json
    echo     "save_crawl_state": true>> settings.json
    echo }>> settings.json
    echo [92mSettings file created![0m
) else (
    echo [92mSettings file already exists![0m
)

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo [92m
echo ===============================================
echo [0m[97m    SETUP COMPLETED SUCCESSFULLY!
echo [0m[97m    Run hungry.bat to start the crawler.
echo [92m===============================================
echo [0m

pause
