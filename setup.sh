#!/bin/bash

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo " HUNGRY CRAWLER SETUP"
echo " ===================="
echo -e "${NC}"

# Check if Python is installed
echo -e "${YELLOW}Verifying Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH.${NC}"
    echo -e "Please install Python from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
echo -e "${GREEN}Python detected!${NC}"

# Create virtual environment if it doesn't exist
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment.${NC}"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created!${NC}"
else
    echo -e "${GREEN}Virtual environment already exists!${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated!${NC}"

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
pip install requests beautifulsoup4 rich pyfiglet markdown pathlib urllib3 certifi
echo -e "${GREEN}Packages installed!${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating system directories...${NC}"
for dir in Results Crawled Exports Logs; do
    if [ ! -d "$dir" ]; then
        mkdir "$dir"
        echo -e "${GREEN}Created $dir directory!${NC}"
    else
        echo -e "${GREEN}$dir directory already exists!${NC}"
    fi
done

# Create settings file if it doesn't exist
echo -e "${YELLOW}Configuring system settings...${NC}"
if [ ! -f "settings.json" ]; then
    cat > settings.json << EOF
{
    "respect_robots_txt": true,
    "crawl_delay": 2,
    "max_pages": 100,
    "timeout": 15,
    "max_retries": 3,
    "user_agent": "HungryCrawler/1.0",
    "blacklist": [],
    "whitelist": [],
    "export_formats": ["json", "csv", "txt", "md"],
    "use_proxies": false,
    "proxies": [],
    "rotate_user_agents": true,
    "save_crawl_state": true
}
EOF
    echo -e "${GREEN}Settings file created!${NC}"
else
    echo -e "${GREEN}Settings file already exists!${NC}"
fi

# Deactivate virtual environment
deactivate

# Make the script executable
chmod +x hungry.sh

echo -e "${GREEN}"
echo "==============================================="
echo -e "${NC}    SETUP COMPLETED SUCCESSFULLY!"
echo -e "    Run ./hungry.sh to start the crawler."
echo -e "${GREEN}==============================================="
echo -e "${NC}"

read -p "Press Enter to exit..."
