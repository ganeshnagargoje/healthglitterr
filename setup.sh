#!/bin/bash
# Setup Script for Medical Health Review System
# For Linux/Mac users

set -e  # Exit on error

echo "========================================"
echo "Medical Health Review System - Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo -e "${YELLOW}Checking prerequisites...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓ Docker found: $DOCKER_VERSION${NC}"
else
    echo -e "${RED}✗ Docker not found!${NC}"
    echo -e "${YELLOW}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓ Docker Compose found: $COMPOSE_VERSION${NC}"
else
    echo -e "${RED}✗ Docker Compose not found!${NC}"
    echo -e "${YELLOW}Please install Docker Compose from: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# Check if Docker is running
if docker ps &> /dev/null; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

echo ""

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠  Please edit .env file with your configuration if needed${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Build and start containers
echo -e "${YELLOW}Building Docker containers...${NC}"
echo -e "${CYAN}(This may take 5-10 minutes on first run)${NC}"
echo -e "${CYAN}(Using binary wheels when available)${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build complete${NC}"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

echo ""

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services started${NC}"
else
    echo -e "${RED}✗ Failed to start services!${NC}"
    exit 1
fi

echo ""

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Check database connection
echo -e "${YELLOW}Testing database connection...${NC}"
if docker-compose exec -T app python -c "from models.database_connection import DatabaseConnection; with DatabaseConnection() as db: print('Database connection successful!')" &> /dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${YELLOW}⚠  Database connection failed - it may need more time to initialize${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Services running:"
echo "  • Application:  http://localhost:8000"
echo "  • Database:     localhost:5432"
echo "  • pgAdmin:      http://localhost:5050 (optional)"
echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop services:    docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Run tests:        docker-compose exec app python -m pytest tests/"
echo ""
echo "Or use Makefile commands:"
echo "  • make start        - Start services"
echo "  • make stop         - Stop services"
echo "  • make test         - Run tests"
echo "  • make help         - Show all commands"
echo ""
echo -e "${YELLOW}For more information, see DOCKER_SETUP_GUIDE.md${NC}"
echo ""
