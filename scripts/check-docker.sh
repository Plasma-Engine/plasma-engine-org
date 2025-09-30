#!/bin/bash

# check-docker.sh - Checks Docker and Docker Compose availability
# Usage: ./scripts/check-docker.sh
# Exit codes:
#   0 - Docker and Docker Compose are available and running
#   1 - Docker is not installed
#   2 - Docker daemon is not running
#   3 - Docker Compose is not installed

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🐋 Checking Docker requirements..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "  • macOS/Windows: https://www.docker.com/products/docker-desktop"
    echo "  • Linux: https://docs.docker.com/engine/install/"
    echo ""
    echo "Or run: ./scripts/setup-docker.sh"
    exit 1
fi

echo "✅ Docker is installed: $(docker --version)"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo ""
    echo "Please start Docker:"
    echo "  • macOS/Windows: Open Docker Desktop application"
    echo "  • Linux: Run 'sudo systemctl start docker' or 'sudo service docker start'"
    echo ""
    echo "If Docker is installed but not starting, try:"
    echo "  • Restart your computer"
    echo "  • Check Docker Desktop settings"
    echo "  • On Linux, ensure your user is in the docker group: 'sudo usermod -aG docker $USER'"
    exit 2
fi

echo "✅ Docker daemon is running"

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose (standalone) is installed: $(docker-compose --version)"
elif docker compose version &> /dev/null 2>&1; then
    echo "✅ Docker Compose (plugin) is installed: $(docker compose version)"
else
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo ""
    echo "Docker Compose is required but not found."
    echo "Please install Docker Compose:"
    echo "  • It's included with Docker Desktop"
    echo "  • Linux: https://docs.docker.com/compose/install/"
    echo ""
    echo "Or run: ./scripts/setup-docker.sh"
    exit 3
fi

# Check Docker system resources
echo ""
echo "📊 Docker System Info:"
docker system df 2>/dev/null || true

# Check if we can run a simple container
echo ""
echo "🧪 Testing Docker functionality..."
if docker run --rm hello-world &> /dev/null; then
    echo "✅ Docker can run containers successfully"
else
    echo -e "${YELLOW}⚠️  Warning: Unable to run test container${NC}"
    echo "   This might indicate permission issues or network problems"
fi

# Check for docker-compose.yml in plasma-engine-infra
INFRA_DIR="$PROJECT_ROOT/plasma-engine-infra"
if [ -d "$INFRA_DIR" ]; then
    if [ -f "$INFRA_DIR/docker-compose.yml" ] || [ -f "$INFRA_DIR/docker-compose.yaml" ]; then
        echo "✅ Docker Compose configuration found in plasma-engine-infra"
    else
        echo -e "${YELLOW}⚠️  Warning: No docker-compose.yml found in plasma-engine-infra${NC}"
        echo "   You may need to clone the infrastructure repository first"
    fi
else
    echo -e "${YELLOW}⚠️  Warning: plasma-engine-infra directory not found${NC}"
    echo "   Run 'make clone-all' to clone all repositories"
fi

echo ""
echo -e "${GREEN}✨ Docker requirements check completed successfully!${NC}"
echo "   You can now run 'make start-infra' to start the infrastructure services"

exit 0