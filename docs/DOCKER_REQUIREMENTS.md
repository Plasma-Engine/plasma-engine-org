# Docker Requirements for Plasma Engine

## Overview

The Plasma Engine infrastructure relies on Docker and Docker Compose to run PostgreSQL, Redis, Neo4j, and other supporting services. This document outlines the Docker requirements and setup instructions.

## System Requirements

### Minimum Requirements
- **Operating System**: macOS, Linux, or Windows 10/11 (with WSL2)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 20GB available for Docker images and volumes
- **CPU**: 4 cores minimum, 8 cores recommended

### Software Requirements
- **Docker Engine**: Version 20.10.0 or later
- **Docker Compose**: Version 2.0.0 or later (included with Docker Desktop)

## Installation

### Quick Setup

The repository includes automated setup scripts:

```bash
# Check if Docker is properly installed and running
make check-docker

# If Docker is not installed, run the setup script
make setup-docker

# Or run the script directly
./scripts/setup-docker.sh
```

### Manual Installation

#### macOS
1. Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Open Docker Desktop from Applications
3. Wait for Docker to start (icon appears in menu bar)

#### Windows
1. Enable WSL2 (Windows Subsystem for Linux 2)
2. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
3. Ensure Docker Desktop is set to use WSL2 backend
4. Start Docker Desktop

#### Linux

##### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

##### RHEL/CentOS/Fedora
```bash
# Install required packages
sudo yum install -y yum-utils

# Set up repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

## Verification

After installation, verify Docker is working:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker daemon is running
docker info

# Run a test container
docker run --rm hello-world
```

## Docker Configuration

### Resource Allocation

For optimal performance, configure Docker Desktop resources:

1. Open Docker Desktop preferences/settings
2. Navigate to Resources section
3. Recommended settings:
   - **Memory**: 8GB minimum
   - **CPUs**: 4 cores minimum
   - **Disk image size**: 60GB minimum

### Docker Daemon Settings

Ensure the Docker daemon is configured to start automatically:

#### macOS/Windows
Docker Desktop handles this automatically.

#### Linux
```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Start Docker daemon
sudo systemctl start docker
```

## Infrastructure Services

The Plasma Engine uses Docker Compose to orchestrate the following services:

| Service    | Port  | Purpose                           |
|------------|-------|-----------------------------------|
| PostgreSQL | 5432  | Primary database (5 databases)    |
| Redis      | 6379  | Cache and message queue           |
| Neo4j      | 7474  | Graph database                    |
|            | 7687  | Neo4j Bolt protocol               |

## Common Docker Commands

```bash
# Start infrastructure
make start-infra

# Stop infrastructure
make stop-infra

# View running containers
make ps

# View logs
make logs

# Clean up Docker resources
docker system prune -a

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune
```

## Troubleshooting

### Docker Daemon Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solutions**:
- macOS/Windows: Open Docker Desktop application
- Linux: Run `sudo systemctl start docker`

### Permission Denied

**Error**: `permission denied while trying to connect to the Docker daemon socket`

**Solution**:
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in for changes to take effect
- Or run with sudo (not recommended)

### Port Already in Use

**Error**: `bind: address already in use`

**Solutions**:
1. Stop conflicting service
2. Change port in docker-compose.yml
3. Find and kill process: `lsof -i :PORT` then `kill -9 PID`

### Insufficient Resources

**Error**: `no space left on device`

**Solutions**:
1. Clean up Docker resources: `docker system prune -a`
2. Increase Docker disk image size in settings
3. Free up system disk space

### Docker Compose Not Found

**Error**: `docker-compose: command not found`

**Solutions**:
- Use Docker Compose V2: `docker compose` (without hyphen)
- Install standalone Docker Compose
- Update Docker Desktop to latest version

## Security Considerations

1. **Never run Docker daemon as root in production**
2. **Use Docker secrets for sensitive data**
3. **Regularly update Docker and base images**
4. **Scan images for vulnerabilities**: `docker scan IMAGE_NAME`
5. **Use specific image tags** instead of `latest`
6. **Implement resource limits** in docker-compose.yml

## Performance Optimization

1. **Use .dockerignore** files to reduce build context
2. **Multi-stage builds** for smaller images
3. **Layer caching** - order Dockerfile commands efficiently
4. **Volume mounts** for development instead of rebuilding
5. **Health checks** to ensure service availability

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Plasma Engine Infrastructure Repository](https://github.com/plasma-engine/plasma-engine-infra)