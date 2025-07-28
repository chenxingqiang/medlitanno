#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Preparing to publish medlitanno to PyPI...${NC}"

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo -e "${RED}Error: twine is not installed. Please install it using 'pip install twine'.${NC}"
    exit 1
fi

# Check if build is installed
if ! command -v build &> /dev/null; then
    echo -e "${RED}Error: build is not installed. Please install it using 'pip install build'.${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo -e "${YELLOW}Building the package...${NC}"
python -m build

# Check the built package
echo -e "${YELLOW}Checking the built package...${NC}"
twine check dist/*

# Ask for confirmation
read -p "Do you want to upload to PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Upload canceled.${NC}"
    exit 0
fi

# Upload to PyPI
echo -e "${YELLOW}Uploading to PyPI...${NC}"
twine upload dist/*

echo -e "${GREEN}Package successfully published to PyPI!${NC}" 