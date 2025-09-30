#!/bin/bash

# Plasma Engine - Development Environment Startup Script
# This script sets up and starts the complete local development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Some services may not work."
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 not found. Some services may not work."
    fi
    
    print_success "Prerequisites check completed"
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cat > .env << EOF
# Plasma Engine Development Environment Configuration

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=plasma_engine

# Redis Configuration  
REDIS_PASSWORD=redis

# Neo4j Configuration
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# pgAdmin Configuration
PGADMIN_EMAIL=admin@plasma.local
PGADMIN_PASSWORD=admin123

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production
NEXTAUTH_SECRET=your-super-secret-nextauth-key-change-in-production

# AI API Keys (Optional - add your own)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
EOF
        print_success "Created .env file"
        print_warning "Please update .env file with your API keys if needed"
    else
        print_status "Using existing .env file"
    fi
}

# Start infrastructure services
start_infrastructure() {
    print_status "Starting infrastructure services..."
    docker-compose up -d postgres redis neo4j pgadmin
    
    print_status "Waiting for databases to be ready..."
    
    # Wait for PostgreSQL
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    
    # Wait for Redis
    for i in {1..30}; do
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    
    print_success "Infrastructure services are ready"
}

# Initialize databases
init_databases() {
    print_status "Initializing databases..."
    
    # Create databases if they don't exist
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE plasma_gateway;" 2>/dev/null || true
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE plasma_research;" 2>/dev/null || true
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE plasma_brand;" 2>/dev/null || true
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE plasma_content;" 2>/dev/null || true
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE plasma_agent;" 2>/dev/null || true
    
    # Enable pgvector extension for research database
    docker-compose exec -T postgres psql -U postgres -d plasma_research -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true
    
    print_success "Databases initialized"
}

# Install dependencies for all services
install_dependencies() {
    print_status "Installing dependencies for all services..."
    
    # Gateway service
    if [ -d "plasma-engine-gateway" ]; then
        print_status "Installing Gateway dependencies..."
        cd plasma-engine-gateway
        if [ -f "package.json" ]; then
            npm install > /dev/null 2>&1
            print_success "Gateway dependencies installed"
        fi
        cd ..
    fi
    
    # Research service  
    if [ -d "plasma-engine-research" ]; then
        print_status "Installing Research dependencies..."
        cd plasma-engine-research
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt > /dev/null 2>&1
            print_success "Research dependencies installed"
        fi
        cd ..
    fi
    
    # Brand service
    if [ -d "plasma-engine-brand" ]; then
        print_status "Installing Brand dependencies..."
        cd plasma-engine-brand
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt > /dev/null 2>&1
            print_success "Brand dependencies installed"  
        fi
        cd ..
    fi
    
    # Content service
    if [ -d "plasma-engine-content" ]; then
        print_status "Installing Content dependencies..."
        cd plasma-engine-content
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt > /dev/null 2>&1
            print_success "Content dependencies installed"
        fi
        cd ..
    fi
    
    # Agent service
    if [ -d "plasma-engine-agent" ]; then
        print_status "Installing Agent dependencies..."
        cd plasma-engine-agent 
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt > /dev/null 2>&1
            print_success "Agent dependencies installed"
        fi
        cd ..
    fi
}

# Start application services
start_services() {
    print_status "Starting application services..."
    docker-compose up -d gateway research brand content agent
    print_success "Application services started"
}

# Display service status
show_status() {
    echo ""
    print_success "🚀 Plasma Engine Development Environment Started!"
    echo ""
    echo "📊 Service URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Gateway (GraphQL):     http://localhost:3000"
    echo "🔬 Research Service:      http://localhost:8000"
    echo "🎨 Brand Service:         http://localhost:8001"
    echo "📝 Content Service:       http://localhost:8002" 
    echo "🤖 Agent Service:         http://localhost:8003"
    echo ""
    echo "🗄️  Database URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🐘 PostgreSQL:            localhost:5432"
    echo "⚡ Redis:                  localhost:6379"
    echo "🕸️  Neo4j Browser:         http://localhost:7474"
    echo "🛠️  pgAdmin:               http://localhost:5050"
    echo ""
    echo "📋 Management Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "View logs:       docker-compose logs -f [service_name]"
    echo "Stop all:        docker-compose down"
    echo "Restart service: docker-compose restart [service_name]"
    echo "Shell access:    docker-compose exec [service_name] /bin/bash"
    echo ""
}

# Main execution flow
main() {
    echo ""
    print_status "🚀 Starting Plasma Engine Development Environment..."
    echo ""
    
    check_prerequisites
    create_env_file
    start_infrastructure
    init_databases
    install_dependencies
    start_services
    show_status
    
    print_success "Development environment is ready! 🎉"
}

# Handle script interruption
cleanup() {
    print_warning "Script interrupted. Stopping services..."
    docker-compose down
    exit 1
}

trap cleanup INT

# Run main function
main "$@"