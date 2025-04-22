#!/bin/bash

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo " HUNGRY CRAWLER"
echo " =============="
echo -e "${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH.${NC}"
    echo -e "Please install Python from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found.${NC}"
    echo -e "Please run ./setup.sh first to install dependencies."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}Starting Hungry Crawler...${NC}"

# Activate virtual environment and run the script
source venv/bin/activate
python3 crawler_scraper.py "$@"

# The script handles its own exit, no need for deactivation here
# as it will never reach this point due to os._exit(0)
