#!/bin/bash

# Plasma Engine - Build Script
# Builds all services and components

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICES=("gateway" "research" "brand" "content" "agent")
BUILD_DIR="build"
PARALLEL_BUILD=${PARALLEL_BUILD:-true}
SKIP_TESTS=${SKIP_TESTS:-false}
VERBOSE=${VERBOSE:-false}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Plasma Engine Build Script

Usage: $0 [OPTIONS] [SERVICE...]

OPTIONS:
    -h, --help          Show this help message
    -s, --sequential    Build services sequentially instead of parallel
    -t, --skip-tests    Skip running tests during build
    -v, --verbose       Verbose output
    -c, --clean         Clean build artifacts before building
    --docker           Build Docker images as well

SERVICES:
    gateway, research, brand, content, agent
    If no services specified, all services will be built

EXAMPLES:
    $0                          # Build all services
    $0 gateway research         # Build only gateway and research services
    $0 --clean --docker         # Clean build with Docker images
    $0 -sv gateway              # Sequential verbose build of gateway only

ENVIRONMENT VARIABLES:
    PARALLEL_BUILD=false        # Disable parallel building
    SKIP_TESTS=true            # Skip tests during build
    VERBOSE=true               # Enable verbose output
EOF
}

# Parse command line arguments
parse_args() {
    local services=()
    local clean_build=false
    local build_docker=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--sequential)
                PARALLEL_BUILD=false
                shift
                ;;
            -t|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--clean)
                clean_build=true
                shift
                ;;
            --docker)
                build_docker=true
                shift
                ;;
            gateway|research|brand|content|agent)
                services+=("$1")
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Use provided services or default to all
    if [[ ${#services[@]} -gt 0 ]]; then
        SERVICES=("${services[@]}")
    fi

    # Set global flags
    if [[ "$clean_build" == true ]]; then
        CLEAN_BUILD=true
    fi

    if [[ "$build_docker" == true ]]; then
        BUILD_DOCKER=true
    fi
}

# Clean build artifacts
clean_artifacts() {
    log_info "Cleaning build artifacts..."

    # Clean Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

    # Clean Node.js artifacts
    find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

    # Clean coverage reports
    find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "coverage.xml" -delete 2>/dev/null || true
    find . -type f -name ".coverage" -delete 2>/dev/null || true

    log_success "Build artifacts cleaned"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python version
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: $python_version"

        if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            log_warning "Python 3.11+ is recommended. Current: $python_version"
        fi
    else
        log_error "Python3 is required but not installed"
        return 1
    fi

    # Check Node.js version for gateway service
    if [[ " ${SERVICES[*]} " =~ " gateway " ]]; then
        if command -v node &> /dev/null; then
            local node_version=$(node --version)
            log_info "Node.js version: $node_version"

            # Check if Node.js version is 20+
            local node_major=$(echo "$node_version" | sed 's/v\([0-9]*\).*/\1/')
            if [[ $node_major -lt 20 ]]; then
                log_warning "Node.js 20+ is recommended. Current: $node_version"
            fi
        else
            log_error "Node.js is required for gateway service but not installed"
            return 1
        fi

        if command -v npm &> /dev/null; then
            local npm_version=$(npm --version)
            log_info "npm version: $npm_version"
        else
            log_error "npm is required but not installed"
            return 1
        fi
    fi

    # Check Docker if building images
    if [[ "${BUILD_DOCKER:-false}" == true ]]; then
        if command -v docker &> /dev/null; then
            local docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
            log_info "Docker version: $docker_version"
        else
            log_error "Docker is required for building images but not installed"
            return 1
        fi
    fi

    log_success "Prerequisites check passed"
}

# Build Python service
build_python_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Building Python service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv" ]]; then
        log_info "Creating virtual environment for $service"
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing production dependencies for $service"
        pip install -r requirements.txt
    fi

    # Install development dependencies if available
    if grep -q "dev.*=" pyproject.toml 2>/dev/null; then
        log_info "Installing development dependencies for $service"
        pip install -e ".[dev]"
    fi

    # Run type checking
    if command -v mypy &> /dev/null; then
        log_info "Running type checking for $service"
        mypy app/ || log_warning "Type checking issues found in $service"
    fi

    # Run linting
    log_info "Running linting for $service"
    ruff check app/ || log_warning "Linting issues found in $service"

    # Run formatting check
    log_info "Checking code formatting for $service"
    black --check app/ || log_warning "Formatting issues found in $service"

    # Run tests if not skipped
    if [[ "$SKIP_TESTS" != true ]] && [[ -d "tests" ]]; then
        log_info "Running tests for $service"
        if [[ "$VERBOSE" == true ]]; then
            pytest tests/ -v --cov=app --cov-report=xml --cov-report=html
        else
            pytest tests/ --cov=app --cov-report=xml
        fi
    fi

    # Security scanning
    if command -v bandit &> /dev/null; then
        log_info "Running security scan for $service"
        bandit -r app/ -ll || log_warning "Security issues found in $service"
    fi

    deactivate
    cd ..

    log_success "Python service built successfully: $service"
}

# Build Node.js service
build_nodejs_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Building Node.js service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Install dependencies
    log_info "Installing dependencies for $service"
    npm ci

    # Run type checking
    if npm run type-check &>/dev/null; then
        log_info "Running type checking for $service"
        npm run type-check
    fi

    # Run linting
    log_info "Running linting for $service"
    npm run lint || log_warning "Linting issues found in $service"

    # Build the application
    log_info "Building application for $service"
    npm run build

    # Run tests if not skipped
    if [[ "$SKIP_TESTS" != true ]]; then
        log_info "Running tests for $service"
        if [[ "$VERBOSE" == true ]]; then
            npm run test:coverage
        else
            npm test
        fi
    fi

    # Security audit
    log_info "Running security audit for $service"
    npm audit --audit-level=high || log_warning "Security vulnerabilities found in $service"

    cd ..

    log_success "Node.js service built successfully: $service"
}

# Build single service
build_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Starting build for service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    # Determine service type and build accordingly
    if [[ "$service" == "gateway" ]]; then
        build_nodejs_service "$service"
    else
        build_python_service "$service"
    fi

    # Build Docker image if requested
    if [[ "${BUILD_DOCKER:-false}" == true ]]; then
        build_docker_image "$service"
    fi
}

# Build Docker image
build_docker_image() {
    local service=$1
    local service_dir="plasma-engine-$service"
    local image_name="plasma-engine/$service"

    log_info "Building Docker image for $service"

    if [[ ! -f "$service_dir/Dockerfile" ]]; then
        log_warning "No Dockerfile found for $service, skipping Docker build"
        return 0
    fi

    # Build the Docker image
    docker build -t "$image_name:latest" "$service_dir/"

    # Tag with commit hash if in git repository
    if git rev-parse --git-dir &>/dev/null; then
        local commit_hash=$(git rev-parse --short HEAD)
        docker tag "$image_name:latest" "$image_name:$commit_hash"
        log_info "Tagged Docker image: $image_name:$commit_hash"
    fi

    # Security scan with Trivy if available
    if command -v trivy &> /dev/null; then
        log_info "Running security scan on Docker image for $service"
        trivy image --exit-code 1 --severity HIGH,CRITICAL "$image_name:latest" || \
            log_warning "Security vulnerabilities found in Docker image for $service"
    fi

    log_success "Docker image built successfully: $image_name"
}

# Build services in parallel
build_parallel() {
    log_info "Building services in parallel: ${SERVICES[*]}"

    local pids=()
    local failed_services=()

    # Start builds in background
    for service in "${SERVICES[@]}"; do
        (
            build_service "$service" 2>&1 | sed "s/^/[$service] /"
            echo $? > "/tmp/build_${service}_status"
        ) &
        pids+=($!)
    done

    # Wait for all builds to complete
    for i in "${!pids[@]}"; do
        local pid=${pids[i]}
        local service=${SERVICES[i]}

        wait $pid
        local status=$(cat "/tmp/build_${service}_status" 2>/dev/null || echo "1")

        if [[ $status -ne 0 ]]; then
            failed_services+=("$service")
        fi

        rm -f "/tmp/build_${service}_status"
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services built successfully in parallel"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Build services sequentially
build_sequential() {
    log_info "Building services sequentially: ${SERVICES[*]}"

    local failed_services=()

    for service in "${SERVICES[@]}"; do
        if ! build_service "$service"; then
            failed_services+=("$service")
            log_error "Build failed for service: $service"
        fi
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services built successfully"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Generate build report
generate_build_report() {
    local start_time=$1
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_info "Generating build report..."

    echo
    echo "============================================"
    echo "           BUILD REPORT"
    echo "============================================"
    echo "Build duration: ${duration}s"
    echo "Services built: ${SERVICES[*]}"
    echo "Parallel build: $PARALLEL_BUILD"
    echo "Tests skipped: $SKIP_TESTS"
    echo "Docker images: ${BUILD_DOCKER:-false}"
    echo "Build completed at: $(date)"
    echo "============================================"
}

# Main function
main() {
    local start_time=$(date +%s)

    # Parse command line arguments
    parse_args "$@"

    log_info "Starting Plasma Engine build process"
    log_info "Services to build: ${SERVICES[*]}"

    # Clean artifacts if requested
    if [[ "${CLEAN_BUILD:-false}" == true ]]; then
        clean_artifacts
    fi

    # Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    # Build services
    if [[ "$PARALLEL_BUILD" == true ]]; then
        if ! build_parallel; then
            log_error "Parallel build failed"
            exit 1
        fi
    else
        if ! build_sequential; then
            log_error "Sequential build failed"
            exit 1
        fi
    fi

    # Generate build report
    generate_build_report $start_time

    log_success "Build process completed successfully!"
}

# Run main function with all arguments
main "$@"