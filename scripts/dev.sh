#!/bin/bash

# Plasma Engine Development Environment Manager
# Provides convenient commands for managing the local development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
OVERRIDE_FILE="docker-compose.override.yml"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# Helper functions
print_header() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}   Plasma Engine Development Environment${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi

    print_success "Docker is installed and running"
}

# Initialize environment file
init_env() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_success "Created .env file from .env.example"
            print_info "Please review and update .env with your configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_info ".env file already exists"
    fi
}

# Start all services
start_services() {
    print_header
    print_info "Starting all services..."

    docker compose up -d

    print_success "All services started!"
    print_info "Waiting for services to be healthy..."

    sleep 5
    docker compose ps

    echo ""
    print_success "Services are running!"
    echo ""
    print_services_urls
}

# Stop all services
stop_services() {
    print_info "Stopping all services..."
    docker compose down
    print_success "All services stopped"
}

# Restart all services
restart_services() {
    stop_services
    start_services
}

# Show service URLs
print_services_urls() {
    echo -e "${BLUE}Service URLs:${NC}"
    echo "  • Gateway API:        http://localhost:8000"
    echo "  • Research API:       http://localhost:8001"
    echo "  • Brand API:          http://localhost:8002"
    echo "  • Content UI:         http://localhost:3000"
    echo "  • Agent UI:           http://localhost:3001"
    echo ""
    echo -e "${BLUE}Development Tools:${NC}"
    echo "  • Adminer (DB UI):    http://localhost:8080"
    echo "  • RabbitMQ Admin:     http://localhost:15672"
    echo "  • Neo4j Browser:      http://localhost:7474"
    echo "  • Flower (Celery):    http://localhost:5555"
    echo "  • MinIO Console:      http://localhost:9001"
    echo "  • Kibana:             http://localhost:5601"
    echo "  • MailHog:            http://localhost:8025"
    echo ""
    echo -e "${BLUE}Default Credentials:${NC}"
    echo "  • Postgres:    plasma / plasma_dev"
    echo "  • Neo4j:       neo4j / neo4j_dev"
    echo "  • RabbitMQ:    plasma / rabbit_dev"
    echo "  • MinIO:       minioadmin / minioadmin"
    echo "  • Flower:      admin / admin"
    echo "  • Test User:   user@plasma.dev / password123"
    echo "  • Admin User:  admin@plasma.dev / password123"
}

# Show logs
show_logs() {
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
        docker compose logs -f --tail=100
    else
        docker compose logs -f --tail=100 "$SERVICE"
    fi
}

# Execute command in a service container
exec_service() {
    SERVICE=$1
    shift
    if [ -z "$SERVICE" ]; then
        print_error "Service name required"
        exit 1
    fi
    docker compose exec "$SERVICE" "$@"
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."

    # Run migrations for each service (when they exist)
    for service in gateway research brand content agent; do
        if docker compose ps | grep -q "plasma-$service"; then
            print_info "Running migrations for $service..."
            # Assuming Python services use alembic
            docker compose exec -T "$service" alembic upgrade head 2>/dev/null || true
        fi
    done

    print_success "Migrations completed"
}

# Reset database
reset_db() {
    print_warning "This will delete all data in the databases!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting databases..."

        docker compose down -v
        docker compose up -d postgres

        sleep 5

        print_info "Re-initializing databases..."
        docker compose up -d

        print_success "Databases reset successfully"
    else
        print_info "Operation cancelled"
    fi
}

# Run tests
run_tests() {
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
        print_info "Running tests for all services..."
        for service in gateway research brand content agent; do
            if docker compose ps | grep -q "plasma-$service"; then
                print_info "Testing $service..."
                docker compose exec -T "$service" pytest 2>/dev/null || true
            fi
        done
    else
        print_info "Running tests for $SERVICE..."
        docker compose exec "$SERVICE" pytest
    fi
}

# Clean up resources
cleanup() {
    print_warning "This will remove all containers, volumes, and networks!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_info "Operation cancelled"
    fi
}

# Show service status
show_status() {
    print_header
    docker compose ps
    echo ""
    print_info "Service Health:"

    for service in postgres redis neo4j rabbitmq gateway research brand content agent; do
        if docker compose ps | grep -q "plasma-$service.*Up.*healthy"; then
            print_success "$service is healthy"
        elif docker compose ps | grep -q "plasma-$service.*Up"; then
            print_warning "$service is running (health check pending)"
        else
            print_error "$service is not running"
        fi
    done
}

# Quick setup for new developers
quick_setup() {
    print_header
    print_info "Running quick setup for new developers..."

    check_docker
    init_env

    print_info "Building Docker images..."
    docker compose build

    print_info "Starting infrastructure services..."
    docker compose up -d postgres redis neo4j rabbitmq

    print_info "Waiting for infrastructure to be ready..."
    sleep 10

    print_info "Starting application services..."
    docker compose up -d

    print_info "Running database migrations..."
    run_migrations

    print_success "Setup complete!"
    echo ""
    print_services_urls
}

# Main script
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    exec)
        shift
        exec_service "$@"
        ;;
    urls)
        print_services_urls
        ;;
    migrate)
        run_migrations
        ;;
    reset-db)
        reset_db
        ;;
    test)
        run_tests "$2"
        ;;
    setup)
        quick_setup
        ;;
    cleanup)
        cleanup
        ;;
    *)
        print_header
        echo "Usage: $0 {start|stop|restart|status|logs|exec|urls|migrate|reset-db|test|setup|cleanup}"
        echo ""
        echo "Commands:"
        echo "  start          Start all services"
        echo "  stop           Stop all services"
        echo "  restart        Restart all services"
        echo "  status         Show service status"
        echo "  logs [service] Show logs (all services or specific)"
        echo "  exec <service> <command>  Execute command in service"
        echo "  urls           Show service URLs and credentials"
        echo "  migrate        Run database migrations"
        echo "  reset-db       Reset all databases (WARNING: destroys data)"
        echo "  test [service] Run tests (all services or specific)"
        echo "  setup          Quick setup for new developers"
        echo "  cleanup        Remove all containers and volumes"
        echo ""
        echo "Examples:"
        echo "  $0 start                  # Start all services"
        echo "  $0 logs gateway           # Show gateway logs"
        echo "  $0 exec gateway bash      # Open bash in gateway container"
        echo "  $0 test research          # Run tests for research service"
        exit 1
        ;;
esac