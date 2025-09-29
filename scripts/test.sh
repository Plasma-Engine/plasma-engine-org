#!/bin/bash

# Plasma Engine - Test Script
# Runs comprehensive tests for all services

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICES=("gateway" "research" "brand" "content" "agent")
TEST_TYPES=("unit" "integration")
COVERAGE_THRESHOLD=90
PARALLEL_TEST=${PARALLEL_TEST:-true}
GENERATE_REPORTS=${GENERATE_REPORTS:-true}
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
Plasma Engine Test Script

Usage: $0 [OPTIONS] [SERVICE...] [TEST_TYPE...]

OPTIONS:
    -h, --help           Show this help message
    -s, --sequential     Run tests sequentially instead of parallel
    -c, --coverage       Generate coverage reports
    -r, --report         Generate detailed test reports
    -v, --verbose        Verbose test output
    -f, --fast           Skip slow tests
    -w, --watch          Watch mode for continuous testing
    --no-cache          Don't use test cache
    --threshold=N       Set coverage threshold (default: 90)

SERVICES:
    gateway, research, brand, content, agent
    If no services specified, all services will be tested

TEST_TYPES:
    unit, integration, e2e
    If no types specified, unit and integration tests will be run

EXAMPLES:
    $0                              # Run all tests for all services
    $0 gateway research             # Test only gateway and research services
    $0 --coverage --report          # Run with coverage and detailed reports
    $0 -v gateway unit             # Verbose unit tests for gateway only
    $0 --watch gateway             # Watch mode for gateway service

ENVIRONMENT VARIABLES:
    PARALLEL_TEST=false            # Disable parallel testing
    GENERATE_REPORTS=true          # Enable test report generation
    VERBOSE=true                   # Enable verbose output
    CI=true                       # Enable CI mode optimizations
EOF
}

# Parse command line arguments
parse_args() {
    local services=()
    local test_types=()
    local fast_mode=false
    local watch_mode=false
    local no_cache=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--sequential)
                PARALLEL_TEST=false
                shift
                ;;
            -c|--coverage)
                GENERATE_COVERAGE=true
                shift
                ;;
            -r|--report)
                GENERATE_REPORTS=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--fast)
                fast_mode=true
                shift
                ;;
            -w|--watch)
                watch_mode=true
                shift
                ;;
            --no-cache)
                no_cache=true
                shift
                ;;
            --threshold=*)
                COVERAGE_THRESHOLD="${1#*=}"
                shift
                ;;
            gateway|research|brand|content|agent)
                services+=("$1")
                shift
                ;;
            unit|integration|e2e)
                test_types+=("$1")
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

    # Use provided test types or default to unit and integration
    if [[ ${#test_types[@]} -gt 0 ]]; then
        TEST_TYPES=("${test_types[@]}")
    fi

    # Set global flags
    if [[ "$fast_mode" == true ]]; then
        FAST_MODE=true
    fi

    if [[ "$watch_mode" == true ]]; then
        WATCH_MODE=true
        PARALLEL_TEST=false  # Watch mode doesn't work well with parallel
    fi

    if [[ "$no_cache" == true ]]; then
        NO_CACHE=true
    fi
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."

    # Create test reports directory
    mkdir -p reports/test-results
    mkdir -p reports/coverage

    # Set environment variables for testing
    export TESTING=true
    export LOG_LEVEL=WARNING

    # CI-specific optimizations
    if [[ "${CI:-false}" == true ]]; then
        export PYTHONUNBUFFERED=1
        export NODE_ENV=test
        PARALLEL_TEST=true
        GENERATE_REPORTS=true
    fi

    log_success "Test environment setup complete"
}

# Test Python service
test_python_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Testing Python service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Activate virtual environment
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
    else
        log_warning "No virtual environment found for $service"
    fi

    # Install test dependencies
    if grep -q "dev.*=" pyproject.toml 2>/dev/null; then
        pip install -e ".[dev]" --quiet
    fi

    # Prepare pytest arguments
    local pytest_args=()

    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v")
    else
        pytest_args+=("-q")
    fi

    if [[ "${GENERATE_COVERAGE:-false}" == true ]]; then
        pytest_args+=(
            "--cov=app"
            "--cov-report=xml:../reports/coverage/$service-coverage.xml"
            "--cov-report=html:../reports/coverage/$service-html"
            "--cov-fail-under=$COVERAGE_THRESHOLD"
        )
    fi

    if [[ "${FAST_MODE:-false}" == true ]]; then
        pytest_args+=("-m" "not slow")
    fi

    if [[ "${NO_CACHE:-false}" == true ]]; then
        pytest_args+=("--cache-clear")
    fi

    if [[ "$GENERATE_REPORTS" == true ]]; then
        pytest_args+=(
            "--junit-xml=../reports/test-results/$service-results.xml"
            "--html=../reports/test-results/$service-report.html"
            "--self-contained-html"
        )
    fi

    # Add test type markers
    for test_type in "${TEST_TYPES[@]}"; do
        case $test_type in
            unit)
                pytest_args+=("tests/unit" "tests/test_*.py")
                ;;
            integration)
                pytest_args+=("tests/integration")
                ;;
            e2e)
                pytest_args+=("tests/e2e")
                ;;
        esac
    done

    # Run tests
    if [[ "${WATCH_MODE:-false}" == true ]]; then
        log_info "Starting watch mode for $service (press Ctrl+C to stop)"
        pytest-watch -- "${pytest_args[@]}" tests/
    else
        pytest "${pytest_args[@]}" tests/ || {
            log_error "Tests failed for $service"
            if [[ -d ".venv" ]]; then
                deactivate
            fi
            cd ..
            return 1
        }
    fi

    # Run additional checks
    if [[ "${FAST_MODE:-false}" != true ]]; then
        # Performance tests
        if [[ -d "tests/performance" ]]; then
            log_info "Running performance tests for $service"
            pytest tests/performance/ --benchmark-only || \
                log_warning "Performance tests failed for $service"
        fi

        # Security tests
        if command -v bandit &> /dev/null; then
            log_info "Running security tests for $service"
            bandit -r app/ -ll || log_warning "Security issues found in $service"
        fi
    fi

    if [[ -d ".venv" ]]; then
        deactivate
    fi
    cd ..

    log_success "Python service tests completed: $service"
}

# Test Node.js service
test_nodejs_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Testing Node.js service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Install dependencies
    npm ci --silent

    # Prepare test environment
    export NODE_ENV=test

    # Run different test types
    local test_success=true

    for test_type in "${TEST_TYPES[@]}"; do
        case $test_type in
            unit)
                log_info "Running unit tests for $service"
                if [[ "${WATCH_MODE:-false}" == true ]]; then
                    npm run test:watch
                elif [[ "${GENERATE_COVERAGE:-false}" == true ]]; then
                    npm run test:coverage || test_success=false
                else
                    npm test || test_success=false
                fi
                ;;
            integration)
                log_info "Running integration tests for $service"
                npm run test:integration 2>/dev/null || \
                    log_warning "No integration tests available for $service"
                ;;
            e2e)
                log_info "Running e2e tests for $service"
                npm run test:e2e 2>/dev/null || \
                    log_warning "No e2e tests available for $service"
                ;;
        esac
    done

    # Generate additional reports
    if [[ "$GENERATE_REPORTS" == true ]]; then
        # Copy coverage reports
        if [[ -d "coverage" ]]; then
            cp -r coverage ../reports/coverage/"$service"-coverage/ 2>/dev/null || true
        fi

        # Generate test report
        if npm run test:report &>/dev/null; then
            npm run test:report
        fi
    fi

    # Run additional checks if not in fast mode
    if [[ "${FAST_MODE:-false}" != true ]]; then
        # Type checking
        if npm run type-check &>/dev/null; then
            log_info "Running type checking for $service"
            npm run type-check || log_warning "Type checking issues found in $service"
        fi

        # Security audit
        log_info "Running security audit for $service"
        npm audit --audit-level=moderate || log_warning "Security vulnerabilities found in $service"

        # Performance tests
        if npm run test:perf &>/dev/null; then
            log_info "Running performance tests for $service"
            npm run test:perf || log_warning "Performance tests failed for $service"
        fi
    fi

    cd ..

    if [[ "$test_success" != true ]]; then
        log_error "Tests failed for $service"
        return 1
    fi

    log_success "Node.js service tests completed: $service"
}

# Test single service
test_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Starting tests for service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    # Determine service type and test accordingly
    if [[ "$service" == "gateway" ]]; then
        test_nodejs_service "$service"
    else
        test_python_service "$service"
    fi
}

# Run tests in parallel
test_parallel() {
    log_info "Running tests in parallel: ${SERVICES[*]}"

    local pids=()
    local failed_services=()

    # Start tests in background
    for service in "${SERVICES[@]}"; do
        (
            test_service "$service" 2>&1 | sed "s/^/[$service] /"
            echo $? > "/tmp/test_${service}_status"
        ) &
        pids+=($!)
    done

    # Wait for all tests to complete
    for i in "${!pids[@]}"; do
        local pid=${pids[i]}
        local service=${SERVICES[i]}

        wait $pid
        local status=$(cat "/tmp/test_${service}_status" 2>/dev/null || echo "1")

        if [[ $status -ne 0 ]]; then
            failed_services+=("$service")
        fi

        rm -f "/tmp/test_${service}_status"
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All service tests passed in parallel"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Run tests sequentially
test_sequential() {
    log_info "Running tests sequentially: ${SERVICES[*]}"

    local failed_services=()

    for service in "${SERVICES[@]}"; do
        if ! test_service "$service"; then
            failed_services+=("$service")
            log_error "Tests failed for service: $service"
        fi
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All service tests passed"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Generate test summary report
generate_test_report() {
    local start_time=$1
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_info "Generating test summary report..."

    local report_file="reports/test-summary.md"
    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# Test Summary Report

**Generated:** $(date)
**Duration:** ${duration}s
**Services:** ${SERVICES[*]}
**Test Types:** ${TEST_TYPES[*]}

## Configuration
- Parallel execution: $PARALLEL_TEST
- Coverage threshold: $COVERAGE_THRESHOLD%
- Fast mode: ${FAST_MODE:-false}
- Watch mode: ${WATCH_MODE:-false}

## Results
EOF

    # Add coverage information if available
    if [[ "${GENERATE_COVERAGE:-false}" == true ]]; then
        echo "" >> "$report_file"
        echo "## Coverage Reports" >> "$report_file"

        for service in "${SERVICES[@]}"; do
            local coverage_file="reports/coverage/$service-coverage.xml"
            if [[ -f "$coverage_file" ]]; then
                echo "- [$service Coverage](coverage/$service-html/index.html)" >> "$report_file"
            fi
        done
    fi

    # Add test result links
    echo "" >> "$report_file"
    echo "## Test Results" >> "$report_file"

    for service in "${SERVICES[@]}"; do
        local result_file="reports/test-results/$service-report.html"
        if [[ -f "$result_file" ]]; then
            echo "- [$service Results](test-results/$service-report.html)" >> "$report_file"
        fi
    done

    echo
    echo "============================================"
    echo "           TEST SUMMARY"
    echo "============================================"
    echo "Test duration: ${duration}s"
    echo "Services tested: ${SERVICES[*]}"
    echo "Test types: ${TEST_TYPES[*]}"
    echo "Parallel execution: $PARALLEL_TEST"
    echo "Coverage threshold: $COVERAGE_THRESHOLD%"
    echo "Report generated: $report_file"
    echo "============================================"

    log_success "Test summary report generated: $report_file"
}

# Main function
main() {
    local start_time=$(date +%s)

    # Parse command line arguments
    parse_args "$@"

    log_info "Starting Plasma Engine test suite"
    log_info "Services to test: ${SERVICES[*]}"
    log_info "Test types: ${TEST_TYPES[*]}"

    # Setup test environment
    setup_test_environment

    # Exit early if in watch mode with multiple services
    if [[ "${WATCH_MODE:-false}" == true ]] && [[ ${#SERVICES[@]} -gt 1 ]]; then
        log_error "Watch mode only supports single service testing"
        exit 1
    fi

    # Run tests
    if [[ "${WATCH_MODE:-false}" == true ]]; then
        # Watch mode for single service
        test_service "${SERVICES[0]}"
    elif [[ "$PARALLEL_TEST" == true ]]; then
        if ! test_parallel; then
            log_error "Parallel testing failed"
            exit 1
        fi
    else
        if ! test_sequential; then
            log_error "Sequential testing failed"
            exit 1
        fi
    fi

    # Generate test report
    if [[ "$GENERATE_REPORTS" == true ]]; then
        generate_test_report $start_time
    fi

    log_success "Test suite completed successfully!"
}

# Run main function with all arguments
main "$@"