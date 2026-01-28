#!/bin/bash
# 
# Publishing Script for quant1024
# 
# Usage:
#   ./publish.sh test     # Publish to TestPyPI
#   ./publish.sh prod     # Publish to PyPI
#

set -e  # Exit on error

echo "🚀 quant1024 Publishing Script"
echo "=============================="
echo ""

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check arguments
if [ "$1" != "test" ] && [ "$1" != "prod" ]; then
    echo -e "${RED}Error: Please specify 'test' or 'prod'${NC}"
    echo "Usage: $0 [test|prod]"
    exit 1
fi

TARGET=$1

echo -e "${YELLOW}Step 1/5: Cleaning old build files...${NC}"
rm -rf dist/ build/ 2>/dev/null || true
rm -rf *.egg-info src/*.egg-info 2>/dev/null || true
echo -e "${GREEN}✅ Clean complete${NC}"
echo ""

echo -e "${YELLOW}Step 2/5: Installing build tools...${NC}"
uv pip install --upgrade build twine
echo -e "${GREEN}✅ Tools ready${NC}"
echo ""

echo -e "${YELLOW}Step 3/5: Building package...${NC}"
uv run python -m build
echo -e "${GREEN}✅ Build complete${NC}"
echo ""

echo -e "${YELLOW}Step 4/5: Checking package...${NC}"
uv run twine check dist/*
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Package check failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Package check passed${NC}"
echo ""

echo -e "${YELLOW}Step 5/5: Uploading package...${NC}"
if [ "$TARGET" = "test" ]; then
    echo "Uploading to TestPyPI..."
    uv run twine upload --repository testpypi dist/*
    echo ""
    echo -e "${GREEN}✅ Published to TestPyPI successfully!${NC}"
    echo ""
    echo "Test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ quant1024"
    echo ""
    echo "After verification, run the following to publish to PyPI:"
    echo "  ./publish.sh prod"
elif [ "$TARGET" = "prod" ]; then
    echo -e "${YELLOW}⚠️  About to publish to PyPI!${NC}"
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    uv run twine upload dist/*
    echo ""
    echo -e "${GREEN}✅ Published to PyPI successfully!${NC}"
    echo ""
    echo "Package published to: https://pypi.org/project/quant1024/"
    echo ""
    echo "Users can install via:"
    echo "  pip install quant1024"
fi

echo ""
echo "🎉 Publishing complete!"

