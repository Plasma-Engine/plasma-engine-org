#!/bin/bash

# Plasma Engine - Development Environment Stop Script
# This script stops all services and optionally cleans up data

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

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean     Remove all data volumes (WARNING: All data will be lost)"
    echo "  --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Stop services, keep data"
    echo "  $0 --clean        # Stop services and remove all data"
}

# Stop all services
stop_services() {
    print_status "Stopping all Plasma Engine services..."
    
    if docker-compose ps -q > /dev/null 2>&1; then
        docker-compose down
        print_success "All services stopped"
    else
        print_warning "No services were running"
    fi
}

# Clean up data volumes
clean_data() {
    print_warning "⚠️  This will permanently delete all database data!"
    print_warning "   - PostgreSQL databases"
    print_warning "   - Redis cache"
    print_warning "   - Neo4j knowledge graphs"
    print_warning "   - pgAdmin settings"
    echo ""
    
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        print_status "Removing all data volumes..."
        
        # Remove all volumes
        docker-compose down -v
        
        # Remove any orphaned volumes
        if docker volume ls -q -f name=plasma-engine-org | grep -q .; then
            docker volume ls -q -f name=plasma-engine-org | xargs docker volume rm
        fi
        
        print_success "All data volumes removed"
    else
        print_status "Data cleanup cancelled"
    fi
}

# Remove Docker images
clean_images() {
    print_status "Removing Plasma Engine Docker images..."
    
    # Remove built images
    if docker images -q plasma-engine* | grep -q .; then
        docker images -q plasma-engine* | xargs docker rmi -f
        print_success "Docker images removed"
    else
        print_warning "No Plasma Engine images found"
    fi
}

# Show final status
show_final_status() {
    echo ""
    print_success "🛑 Plasma Engine Development Environment Stopped"
    echo ""
    
    # Show remaining containers
    if docker ps -q --filter "label=com.docker.compose.project=plasma-engine-org" | grep -q .; then
        print_warning "Some containers are still running:"
        docker ps --filter "label=com.docker.compose.project=plasma-engine-org"
    else
        print_success "No containers running"
    fi
    
    echo ""
    echo "📋 To restart the environment:"
    echo "   ./scripts/dev-start.sh"
    echo ""
}

# Main execution flow
main() {
    local clean=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    echo ""
    print_status "🛑 Stopping Plasma Engine Development Environment..."
    echo ""
    
    stop_services
    
    if [ "$clean" = true ]; then
        clean_data
        clean_images
    fi
    
    show_final_status
}

# Run main function
main "$@"