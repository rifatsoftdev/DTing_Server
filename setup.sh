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

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env file"
    else
        rm .env
    fi
else
    echo -e "${GREEN}✓ Creating .env file...${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Server Version and Debug mode
VERSION=1.0.8
DEBUG=True
LOG_LEVEL=info
APP_BASE_URL=http://192.168.1.100:8000

# External API
SMS_SERVER=http://localhost:8001

# DataBase configuration
DATABASE_URL="sqlite:///./database.db"

# Email configuration
EMAIL_ADDRESS=example@gmail.com
EMAIL_PASSWORD=example_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME=cloudinary_cloud_name
CLOUDINARY_API_KEY=cloudinary_api_key
CLOUDINARY_API_SECRET=cloudinary_api_secret

# Twilio configuration
ACCOUNT_SID=twilio_account_sid
AUTH_TOKEN=twilio_auth_token

# JWT configuration
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_EXPIRE=10
REFRESH_EXPIRE=30
OTP_TOKEN_EXPIRE_MIN=5
PASS_RST_TOKEN_EXPIRE_MIN=15

# Redis configuration
REDIS_URL=redis://localhost:6379
EMAIL_QUEUE_NAME=email_queue
EMAIL_FAILED_QUEUE_NAME=email_failed_queue
SMS_QUEUE_NAME=sms_queue
SMS_FAILED_QUEUE_NAME=sms_failed_queue
EMAIL_MAX_ATTEMPTS=5
EMAIL_WORKER_POLL_TIMEOUT=5
SMS_MAX_ATTEMPTS=5
SMS_WORKER_POLL_TIMEOUT=5

# Salt for password hashing
SALT=random_salt_value

# Firebase configuration
FIREBASE_ADMINSDK={}
GOOGLE_CLIENT_ID=google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=google-client-secret

# CORS configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Default admin
DEFAULT_ADMIN_EMAIL=user@example.com
DEFAULT_ADMIN_PHONE=01700000000
DEFAULT_ADMIN_PASSWORD=Admin@123
DEFAULT_ADMIN_NAME=Admin DTing

# Default user
DEFAULT_USER_EMAIL=user@example.com
DEFAULT_USER_PHONE=01700000000
DEFAULT_USER_PASSWORD=User@123
DEFAULT_USER_NAME=DTing

EOF
    echo -e "${GREEN}✓ .env file created successfully!${NC}"
fi

echo ""
echo "=========================================="
echo "  Setup Options"
echo "=========================================="
echo ""
echo "1. Setup with Docker / Docker Compose"
echo "2. Setup without Docker (Manual)"
echo ""
read -p "Choose an option (1 or 2): " -n 1 -r
echo
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
    
    echo -e "${YELLOW}📝 Please update the .env file with your credentials before proceeding.${NC}"
    echo ""
    read -p "Have you updated the .env file? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update .env file and run this script again."
        exit 0
    fi
    
    echo ""
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
    echo -e "🚀 DTin Server is running at:"
    echo -e "   ${GREEN}http://localhost:8000${NC}"
    echo ""n
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
    echo -e "${YELLOW}📝 Please update the .env file with your credentials before proceeding.${NC}"
    echo ""
    read -p "Have you updated the .env file? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update .env file and run this script again."
        exit 0
    fi
    
    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "=========================================="
    echo "  Manual Setup Complete"
    echo "=========================================="
    echo ""
    echo "To start the server, run:"
    echo -e "   ${GREEN}source venv/bin/activate${NC}"
    echo -e "   ${GREEN}python run.py${NC}"
    echo ""
    echo "Or use Uvicorn directly:"
    echo -e "   ${GREEN}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
    echo ""
    
else
    echo -e "${RED}Invalid option. Please choose 1 or 2.${NC}"
    exit 1
fi

echo ""
