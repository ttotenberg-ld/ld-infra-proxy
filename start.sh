#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LD Infra Proxy Demo...${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Cleaning up processes...${NC}"
    kill $OLD_PID $NEW_PID $MIDDLEWARE_PID 2>/dev/null
    wait $OLD_PID $NEW_PID $MIDDLEWARE_PID 2>/dev/null
    echo -e "${GREEN}Cleanup complete.${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found. Please copy .env.example to .env and add your LaunchDarkly SDK key.${NC}"
    exit 1
fi

# Start old service
echo -e "${YELLOW}Starting old service (port 8001)...${NC}"
python old_service.py &
OLD_PID=$!

# Start new service
echo -e "${YELLOW}Starting new service (port 8002)...${NC}"
python new_service.py &
NEW_PID=$!

# Start middleware
echo -e "${YELLOW}Starting middleware (port 8000)...${NC}"
python middleware.py &
MIDDLEWARE_PID=$!

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 3

# Check if services are running
if ! kill -0 $OLD_PID 2>/dev/null; then
    echo -e "${RED}Error: Old service failed to start${NC}"
    exit 1
fi

if ! kill -0 $NEW_PID 2>/dev/null; then
    echo -e "${RED}Error: New service failed to start${NC}"
    exit 1
fi

if ! kill -0 $MIDDLEWARE_PID 2>/dev/null; then
    echo -e "${RED}Error: Middleware failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}Starting test script...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Run test script
python test_middleware.py 