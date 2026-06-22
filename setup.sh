#!/bin/bash

set -e

echo "=========================================="
echo "  DTing Server Setup Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==========================================
# Non-interactive / CI detection
# ==========================================
# Auto-detected when run inside GitHub Actions (CI=true, GITHUB_ACTIONS=true)
# or any environment without a tty. Can also be forced manually:
#   NONINTERACTIVE=true ./setup.sh
if [ "$NONINTERACTIVE" = "true" ] || [ "$CI" = "true" ] || [ "$GITHUB_ACTIONS" = "true" ] || [ ! -t 0 ]; then
    NONINTERACTIVE=true
else
    NONINTERACTIVE=false
fi

# Default used ONLY when running non-interactively (override via env var).
SETUP_MODE="${SETUP_MODE:-2}" # 1 = Docker, 2 = Manual (venv)

if [ "$NONINTERACTIVE" = "true" ]; then
    echo -e "${YELLOW}ℹ️  Non-interactive mode detected (CI/no tty). Prompts will be auto-answered.${NC}"
    echo ""
fi

# ask "<prompt text>" "<default answer used in non-interactive mode>"
# Sets $REPLY just like a `read -p ... -n 1 -r` call would.
ask() {
    local prompt="$1"
    local default="$2"
    if [ "$NONINTERACTIVE" = "true" ]; then
        REPLY="$default"
        echo "$prompt $default  (auto-answered)"
    else
        read -p "$prompt " -n 1 -r
        echo
    fi
}

# ==========================================
# .env check — existence is the only gate.
# Creating/updating .env is the user's responsibility, not this
# script's. We never auto-generate it or ask "did you update it?".
# ==========================================
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found.${NC}"
    echo ""
    echo "This script will not create one for you — please set it up first."
    echo "You can copy the provided template and fill in your own values:"
    echo -e "   ${GREEN}cp demo.env .env${NC}"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✓ .env file found. Proceeding...${NC}"
echo ""

echo "=========================================="
echo "  Setup Options"
echo "=========================================="
echo ""
echo "1. Setup with Docker / Docker Compose"
echo "2. Setup without Docker (Manual)"
echo ""
ask "Choose an option (1 or 2):" "$SETUP_MODE"
echo ""

if [[ $REPLY =~ ^[1]$ ]]; then
    echo -e "${GREEN}Setting up with Docker...${NC}"

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi

    # Check if Docker Compose is installed
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}✗ Docker Compose is not installed.${NC}"
        echo "You can either install Docker Compose or run this script again and choose option 2 for manual setup."
        exit 1
    fi

    echo -e "${GREEN}Building Docker image...${NC}"
    $COMPOSE_CMD build

    echo ""
    echo -e "${GREEN}Starting DTing Server...${NC}"
    $COMPOSE_CMD up -d

    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "=========================================="
    echo "  Docker Setup Complete"
    echo "=========================================="
    echo ""
    echo -e "🚀 DTing Server is running at:"
    echo -e "   ${GREEN}http://localhost:8000${NC}"
    echo ""
    echo -e "📚 API Documentation:"
    echo -e "   ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "🔐 Admin Login:"
    echo -e "   ${GREEN}http://localhost:8000/admin/login${NC}"
    echo ""
    echo "View logs:"
    echo -e "   ${GREEN}$COMPOSE_CMD logs -f${NC}"
    echo ""
    echo "Stop server:"
    echo -e "   ${GREEN}$COMPOSE_CMD down${NC}"
    echo ""

elif [[ $REPLY =~ ^[2]$ ]]; then
    echo -e "${GREEN}Setting up without Docker...${NC}"

    # Check if Python 3.10+ is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 is not installed. Please install Python 3.10 or newer.${NC}"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "Python version: $PYTHON_VERSION"

    echo ""
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv

    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate

    echo -e "${GREEN}Upgrading pip...${NC}"
    pip install --upgrade pip

    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -r requirements.txt

    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "=========================================="
    echo "  Manual Setup Complete"
    echo "=========================================="
    echo ""
    echo "Starting the server..."
    echo -e "   ${GREEN}uvicorn app.main:app --host 0.0.0.0 --port 8000${NC}"
    echo ""
    uvicorn app.main:app --host 0.0.0.0 --port 8000

else
    echo -e "${RED}Invalid option. Please choose 1 or 2.${NC}"
    exit 1
fi

echo ""