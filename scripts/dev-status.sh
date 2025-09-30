#!/bin/bash

# Plasma Engine - Development Environment Status Checker
# This script checks the status of all services and provides health information

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

# Check if Docker is running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    return 0
}

# Check service health
check_service_health() {
    local service=$1
    local port=$2
    local path=${3:-/health}
    
    if curl -s -f "http://localhost:${port}${path}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Check database connection
check_database() {
    local db_name=$1
    
    if docker-compose exec -T postgres psql -U postgres -d "$db_name" -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Connection failed${NC}"
        return 1
    fi
}

# Get container resource usage
get_container_stats() {
    local service=$1
    local container_name="plasma-${service}"
    
    if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
        local stats=$(docker stats "$container_name" --no-stream --format "CPU: {{.CPUPerc}} | Memory: {{.MemUsage}}")
        echo -e "${BLUE}$stats${NC}"
    else
        echo -e "${RED}Container not running${NC}"
    fi
}

# Main status check
main() {
    echo ""
    print_status "🔍 Plasma Engine Development Environment Status"
    echo ""
    
    # Check Docker
    if ! check_docker; then
        exit 1
    fi
    
    # Header
    printf "%-20s %-15s %-15s %-15s %-40s\n" "Service" "Container" "Port" "Health" "Resources"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Infrastructure Services
    echo -e "\n${BLUE}🏗️  Infrastructure Services${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # PostgreSQL
    printf "%-20s" "PostgreSQL"
    if docker-compose ps postgres | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "5432"
        printf "%-15s" "$(check_database plasma_gateway > /dev/null 2>&1 && echo -e "${GREEN}✅ Connected${NC}" || echo -e "${RED}❌ Failed${NC}")"
        printf "%-40s" "$(get_container_stats postgres)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "5432"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Redis
    printf "%-20s" "Redis"
    if docker-compose ps redis | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "6379"
        printf "%-15s" "$(docker-compose exec -T redis redis-cli ping > /dev/null 2>&1 && echo -e "${GREEN}✅ PONG${NC}" || echo -e "${RED}❌ Failed${NC}")"
        printf "%-40s" "$(get_container_stats redis)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "6379"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Neo4j
    printf "%-20s" "Neo4j"
    if docker-compose ps neo4j | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "7474/7687"
        printf "%-15s" "$(curl -s -f http://localhost:7474 > /dev/null 2>&1 && echo -e "${GREEN}✅ Ready${NC}" || echo -e "${RED}❌ Failed${NC}")"
        printf "%-40s" "$(get_container_stats neo4j)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "7474/7687"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Application Services
    echo -e "\n${BLUE}🚀 Application Services${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Gateway Service
    printf "%-20s" "Gateway"
    if docker-compose ps gateway | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "3000"
        printf "%-15s" "$(check_service_health gateway 3000)"
        printf "%-40s" "$(get_container_stats gateway)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "3000"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Research Service
    printf "%-20s" "Research"
    if docker-compose ps research | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "8000"
        printf "%-15s" "$(check_service_health research 8000)"
        printf "%-40s" "$(get_container_stats research)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "8000"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Brand Service
    printf "%-20s" "Brand"
    if docker-compose ps brand | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "8001"
        printf "%-15s" "$(check_service_health brand 8001)"
        printf "%-40s" "$(get_container_stats brand)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "8001"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Content Service
    printf "%-20s" "Content"
    if docker-compose ps content | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "8002"
        printf "%-15s" "$(check_service_health content 8002)"
        printf "%-40s" "$(get_container_stats content)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "8002"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Agent Service
    printf "%-20s" "Agent"
    if docker-compose ps agent | grep -q "Up"; then
        printf "%-15s" "$(echo -e "${GREEN}Running${NC}")"
        printf "%-15s" "8003"
        printf "%-15s" "$(check_service_health agent 8003)"
        printf "%-40s" "$(get_container_stats agent)"
    else
        printf "%-15s" "$(echo -e "${RED}Stopped${NC}")"
        printf "%-15s" "8003"
        printf "%-15s" "$(echo -e "${RED}❌ Down${NC}")"
        printf "%-40s" "Not running"
    fi
    echo ""
    
    # Database Status
    echo -e "\n${BLUE}🗄️  Database Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if docker-compose ps postgres | grep -q "Up"; then
        databases=("plasma_gateway" "plasma_research" "plasma_brand" "plasma_content" "plasma_agent")
        for db in "${databases[@]}"; do
            printf "%-20s" "$db"
            check_database "$db"
        done
    else
        print_warning "PostgreSQL is not running - cannot check database status"
    fi
    
    # Quick Actions
    echo -e "\n${BLUE}📋 Quick Actions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Start all services:      ./scripts/dev-start.sh"
    echo "Stop all services:       ./scripts/dev-stop.sh"
    echo "View logs:               docker-compose logs -f [service_name]"
    echo "Restart service:         docker-compose restart [service_name]"
    echo "Shell access:            docker-compose exec [service_name] /bin/bash"
    echo ""
}

# Run main function
main "$@"