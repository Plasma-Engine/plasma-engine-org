#!/bin/bash

# setup-docker.sh - Helps install and configure Docker
# Usage: ./scripts/setup-docker.sh
# Supports: macOS, Ubuntu/Debian, RHEL/CentOS/Fedora, Arch Linux

set -e

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🐋 Docker Setup Script"
echo "====================="

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ -f /etc/debian_version ]]; then
        echo "debian"
    elif [[ -f /etc/redhat-release ]]; then
        echo "redhat"
    elif [[ -f /etc/arch-release ]]; then
        echo "arch"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo "Detected OS: $OS"

# Function to check if Docker is already installed
check_docker_installed() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker is already installed: $(docker --version)${NC}"
        return 0
    else
        return 1
    fi
}

# Function to install Docker on macOS
install_docker_macos() {
    echo -e "${BLUE}Installing Docker Desktop for macOS...${NC}"

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Homebrew is not installed. Installing Homebrew first...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install Docker Desktop using Homebrew
    brew install --cask docker

    echo -e "${GREEN}✅ Docker Desktop installed${NC}"
    echo "Please open Docker Desktop from Applications to complete setup"
    open -a Docker
}

# Function to install Docker on Ubuntu/Debian
install_docker_debian() {
    echo -e "${BLUE}Installing Docker Engine for Ubuntu/Debian...${NC}"

    # Update package index
    sudo apt-get update

    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add user to docker group
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✅ Docker Engine installed${NC}"
    echo -e "${YELLOW}Note: You need to log out and back in for group changes to take effect${NC}"
}

# Function to install Docker on RHEL/CentOS/Fedora
install_docker_redhat() {
    echo -e "${BLUE}Installing Docker Engine for RHEL/CentOS/Fedora...${NC}"

    # Remove old versions
    sudo yum remove -y docker \
        docker-client \
        docker-client-latest \
        docker-common \
        docker-latest \
        docker-latest-logrotate \
        docker-logrotate \
        docker-engine

    # Install required packages
    sudo yum install -y yum-utils

    # Set up the repository
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

    # Install Docker Engine
    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker

    # Add user to docker group
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✅ Docker Engine installed${NC}"
    echo -e "${YELLOW}Note: You need to log out and back in for group changes to take effect${NC}"
}

# Function to install Docker on Arch Linux
install_docker_arch() {
    echo -e "${BLUE}Installing Docker for Arch Linux...${NC}"

    # Install Docker
    sudo pacman -S --noconfirm docker docker-compose

    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker

    # Add user to docker group
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✅ Docker installed${NC}"
    echo -e "${YELLOW}Note: You need to log out and back in for group changes to take effect${NC}"
}

# Function to start Docker daemon
start_docker_daemon() {
    echo "Starting Docker daemon..."

    if [[ "$OS" == "macos" ]]; then
        echo "Opening Docker Desktop..."
        open -a Docker
        echo "Please wait for Docker Desktop to start (this may take a minute)"
        echo "You can check the status with: docker info"
    else
        # Linux systems
        if sudo systemctl is-active --quiet docker; then
            echo -e "${GREEN}✅ Docker daemon is already running${NC}"
        else
            echo "Starting Docker service..."
            sudo systemctl start docker
            sudo systemctl enable docker
            echo -e "${GREEN}✅ Docker daemon started${NC}"
        fi
    fi
}

# Function to verify Docker installation
verify_docker() {
    echo ""
    echo "Verifying Docker installation..."

    # Wait a bit for Docker to start (especially on macOS)
    if [[ "$OS" == "macos" ]]; then
        echo "Waiting for Docker to start..."
        for i in {1..30}; do
            if docker info &> /dev/null; then
                break
            fi
            sleep 2
        done
    fi

    if docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker is running successfully${NC}"
        docker --version
        docker compose version 2>/dev/null || docker-compose --version 2>/dev/null || true

        # Test with hello-world
        echo ""
        echo "Running test container..."
        if docker run --rm hello-world &> /dev/null; then
            echo -e "${GREEN}✅ Docker can run containers${NC}"
        else
            echo -e "${YELLOW}⚠️  Warning: Could not run test container${NC}"
        fi
    else
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo "Please check Docker installation and try starting it manually"
        exit 1
    fi
}

# Function to show post-installation instructions
show_instructions() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}Docker Setup Complete!${NC}"
    echo "=================================="
    echo ""
    echo "Next steps:"

    if [[ "$OS" == "macos" ]]; then
        echo "1. Docker Desktop should be running in your menu bar"
        echo "2. You can now run: make start-infra"
    else
        echo "1. Log out and back in for group changes to take effect"
        echo "2. Then run: make start-infra"
        echo ""
        echo "Or run without logging out:"
        echo "  newgrp docker"
        echo "  make start-infra"
    fi

    echo ""
    echo "Useful Docker commands:"
    echo "  docker info          - Check Docker system information"
    echo "  docker ps            - List running containers"
    echo "  docker images        - List Docker images"
    echo "  docker system prune  - Clean up unused resources"
}

# Main installation flow
main() {
    echo ""

    # Check if Docker is already installed
    if check_docker_installed; then
        echo ""
        read -p "Docker is already installed. Do you want to start/restart the Docker daemon? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_docker_daemon
            verify_docker
            show_instructions
        else
            echo "Checking Docker status..."
            verify_docker
        fi
        exit 0
    fi

    # Install Docker based on OS
    case "$OS" in
        macos)
            install_docker_macos
            ;;
        debian)
            install_docker_debian
            ;;
        redhat)
            install_docker_redhat
            ;;
        arch)
            install_docker_arch
            ;;
        *)
            echo -e "${RED}Unsupported operating system${NC}"
            echo "Please install Docker manually:"
            echo "  https://docs.docker.com/get-docker/"
            exit 1
            ;;
    esac

    # Start Docker daemon
    start_docker_daemon

    # Verify installation
    verify_docker

    # Show instructions
    show_instructions
}

# Run main function
main