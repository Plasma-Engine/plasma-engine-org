#!/bin/bash

# Plasma Engine - Lint Script
# Runs comprehensive linting and code quality checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICES=("gateway" "research" "brand" "content" "agent")
FIX_ISSUES=${FIX_ISSUES:-false}
STRICT_MODE=${STRICT_MODE:-false}
PARALLEL_LINT=${PARALLEL_LINT:-true}
GENERATE_REPORTS=${GENERATE_REPORTS:-true}

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
Plasma Engine Lint Script

Usage: $0 [OPTIONS] [SERVICE...]

OPTIONS:
    -h, --help          Show this help message
    -f, --fix           Fix auto-fixable issues
    -s, --strict        Strict mode (fail on warnings)
    --sequential        Run linting sequentially instead of parallel
    --no-reports        Don't generate lint reports
    -c, --config        Show current linting configuration
    --check-only        Only check, don't format (dry-run)

SERVICES:
    gateway, research, brand, content, agent
    If no services specified, all services will be linted

EXAMPLES:
    $0                          # Lint all services
    $0 gateway research         # Lint only gateway and research services
    $0 --fix --strict          # Fix issues and use strict mode
    $0 -f gateway              # Fix issues in gateway service only

ENVIRONMENT VARIABLES:
    FIX_ISSUES=true            # Automatically fix issues
    STRICT_MODE=true           # Enable strict mode
    PARALLEL_LINT=false        # Disable parallel linting
    CI=true                    # Enable CI mode optimizations
EOF
}

# Parse command line arguments
parse_args() {
    local services=()
    local check_only=false
    local show_config=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--fix)
                FIX_ISSUES=true
                shift
                ;;
            -s|--strict)
                STRICT_MODE=true
                shift
                ;;
            --sequential)
                PARALLEL_LINT=false
                shift
                ;;
            --no-reports)
                GENERATE_REPORTS=false
                shift
                ;;
            -c|--config)
                show_config=true
                shift
                ;;
            --check-only)
                check_only=true
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
    if [[ "$check_only" == true ]]; then
        CHECK_ONLY=true
        FIX_ISSUES=false
    fi

    if [[ "$show_config" == true ]]; then
        SHOW_CONFIG=true
    fi
}

# Show configuration
show_configuration() {
    echo "============================================"
    echo "           LINT CONFIGURATION"
    echo "============================================"
    echo "Services: ${SERVICES[*]}"
    echo "Fix issues: $FIX_ISSUES"
    echo "Strict mode: $STRICT_MODE"
    echo "Parallel execution: $PARALLEL_LINT"
    echo "Generate reports: $GENERATE_REPORTS"
    echo "Check only: ${CHECK_ONLY:-false}"
    echo
    echo "Python tools:"
    echo "  - black (formatting)"
    echo "  - ruff (linting)"
    echo "  - mypy (type checking)"
    echo "  - bandit (security)"
    echo "  - isort (import sorting)"
    echo
    echo "Node.js tools:"
    echo "  - eslint (linting)"
    echo "  - prettier (formatting)"
    echo "  - typescript (type checking)"
    echo
    echo "============================================"
}

# Setup lint environment
setup_lint_environment() {
    log_info "Setting up lint environment..."

    # Create reports directory
    if [[ "$GENERATE_REPORTS" == true ]]; then
        mkdir -p reports/lint-results
    fi

    # CI-specific optimizations
    if [[ "${CI:-false}" == true ]]; then
        PARALLEL_LINT=true
        GENERATE_REPORTS=true
        STRICT_MODE=true
    fi

    log_success "Lint environment setup complete"
}

# Lint Python service
lint_python_service() {
    local service=$1
    local service_dir="plasma-engine-$service"
    local exit_code=0

    log_info "Linting Python service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Activate virtual environment if available
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
    fi

    # Install linting tools
    pip install --quiet black ruff mypy bandit isort

    local report_file="../reports/lint-results/$service-python.txt"
    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "# Python Lint Report for $service" > "$report_file"
        echo "Generated: $(date)" >> "$report_file"
        echo >> "$report_file"
    fi

    # Import sorting with isort
    log_info "Checking import sorting for $service"
    if [[ "${CHECK_ONLY:-false}" == true ]]; then
        isort --check-only --diff app/ || {
            log_warning "Import sorting issues found in $service"
            exit_code=1
        }
    elif [[ "$FIX_ISSUES" == true ]]; then
        isort app/ || {
            log_warning "Import sorting failed for $service"
            exit_code=1
        }
    else
        isort --check-only app/ || {
            log_warning "Import sorting issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Code formatting with black
    log_info "Checking code formatting for $service"
    if [[ "${CHECK_ONLY:-false}" == true ]]; then
        black --check --diff app/ || {
            log_warning "Formatting issues found in $service"
            exit_code=1
        }
    elif [[ "$FIX_ISSUES" == true ]]; then
        black app/ || {
            log_warning "Formatting failed for $service"
            exit_code=1
        }
    else
        black --check app/ || {
            log_warning "Formatting issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Linting with ruff
    log_info "Running ruff linting for $service"
    local ruff_args=("check" "app/")

    if [[ "$FIX_ISSUES" == true ]]; then
        ruff_args+=("--fix")
    fi

    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "## Ruff Linting Results" >> "$report_file"
        ruff "${ruff_args[@]}" --output-format=text >> "$report_file" 2>&1 || {
            log_warning "Ruff linting issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
        echo >> "$report_file"
    else
        ruff "${ruff_args[@]}" || {
            log_warning "Ruff linting issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Type checking with mypy
    log_info "Running type checking for $service"
    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "## MyPy Type Checking Results" >> "$report_file"
        mypy app/ --no-error-summary >> "$report_file" 2>&1 || {
            log_warning "Type checking issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
        echo >> "$report_file"
    else
        mypy app/ --no-error-summary || {
            log_warning "Type checking issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Security linting with bandit
    log_info "Running security linting for $service"
    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "## Bandit Security Analysis Results" >> "$report_file"
        bandit -r app/ -f txt >> "$report_file" 2>&1 || {
            log_warning "Security issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
        echo >> "$report_file"
    else
        bandit -r app/ -ll || {
            log_warning "Security issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Additional quality checks
    if command -v vulture &> /dev/null; then
        log_info "Checking for dead code in $service"
        if [[ "$GENERATE_REPORTS" == true ]]; then
            echo "## Dead Code Analysis (Vulture)" >> "$report_file"
            vulture app/ >> "$report_file" 2>&1 || true
            echo >> "$report_file"
        else
            vulture app/ || log_warning "Dead code found in $service"
        fi
    fi

    # Code complexity analysis
    if command -v radon &> /dev/null; then
        log_info "Analyzing code complexity for $service"
        if [[ "$GENERATE_REPORTS" == true ]]; then
            echo "## Code Complexity Analysis (Radon)" >> "$report_file"
            echo "### Cyclomatic Complexity" >> "$report_file"
            radon cc app/ -a >> "$report_file" 2>&1 || true
            echo >> "$report_file"
            echo "### Maintainability Index" >> "$report_file"
            radon mi app/ >> "$report_file" 2>&1 || true
            echo >> "$report_file"
        fi
    fi

    if [[ -d ".venv" ]]; then
        deactivate
    fi
    cd ..

    if [[ $exit_code -eq 0 ]]; then
        log_success "Python linting completed for $service"
    else
        log_error "Python linting failed for $service"
    fi

    return $exit_code
}

# Lint Node.js service
lint_nodejs_service() {
    local service=$1
    local service_dir="plasma-engine-$service"
    local exit_code=0

    log_info "Linting Node.js service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    cd "$service_dir"

    # Install dependencies
    npm ci --silent

    local report_file="../reports/lint-results/$service-nodejs.txt"
    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "# Node.js Lint Report for $service" > "$report_file"
        echo "Generated: $(date)" >> "$report_file"
        echo >> "$report_file"
    fi

    # ESLint
    log_info "Running ESLint for $service"
    local eslint_args=("src/**/*.{js,ts,tsx}")

    if [[ "$FIX_ISSUES" == true ]]; then
        eslint_args+=("--fix")
    fi

    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "## ESLint Results" >> "$report_file"
        npx eslint "${eslint_args[@]}" --format=compact >> "$report_file" 2>&1 || {
            log_warning "ESLint issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
        echo >> "$report_file"
    else
        npx eslint "${eslint_args[@]}" || {
            log_warning "ESLint issues found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Prettier formatting
    if [[ -f ".prettierrc" ]] || [[ -f "prettier.config.js" ]]; then
        log_info "Checking Prettier formatting for $service"
        if [[ "${CHECK_ONLY:-false}" == true ]]; then
            npx prettier --check "src/**/*.{js,ts,tsx,json}" || {
                log_warning "Prettier formatting issues found in $service"
                exit_code=1
            }
        elif [[ "$FIX_ISSUES" == true ]]; then
            npx prettier --write "src/**/*.{js,ts,tsx,json}" || {
                log_warning "Prettier formatting failed for $service"
                exit_code=1
            }
        else
            npx prettier --check "src/**/*.{js,ts,tsx,json}" || {
                log_warning "Prettier formatting issues found in $service"
                if [[ "$STRICT_MODE" == true ]]; then
                    exit_code=1
                fi
            }
        fi
    fi

    # TypeScript type checking
    if [[ -f "tsconfig.json" ]]; then
        log_info "Running TypeScript type checking for $service"
        if [[ "$GENERATE_REPORTS" == true ]]; then
            echo "## TypeScript Type Checking Results" >> "$report_file"
            npx tsc --noEmit >> "$report_file" 2>&1 || {
                log_warning "TypeScript type checking issues found in $service"
                if [[ "$STRICT_MODE" == true ]]; then
                    exit_code=1
                fi
            }
            echo >> "$report_file"
        else
            npx tsc --noEmit || {
                log_warning "TypeScript type checking issues found in $service"
                if [[ "$STRICT_MODE" == true ]]; then
                    exit_code=1
                fi
            }
        fi
    fi

    # Security audit
    log_info "Running npm security audit for $service"
    if [[ "$GENERATE_REPORTS" == true ]]; then
        echo "## NPM Security Audit Results" >> "$report_file"
        npm audit --audit-level=moderate >> "$report_file" 2>&1 || {
            log_warning "Security vulnerabilities found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
        echo >> "$report_file"
    else
        npm audit --audit-level=high || {
            log_warning "Security vulnerabilities found in $service"
            if [[ "$STRICT_MODE" == true ]]; then
                exit_code=1
            fi
        }
    fi

    # Bundle analyzer (if available)
    if npm run analyze &>/dev/null; then
        log_info "Running bundle analysis for $service"
        if [[ "$GENERATE_REPORTS" == true ]]; then
            echo "## Bundle Analysis" >> "$report_file"
            npm run analyze >> "$report_file" 2>&1 || true
            echo >> "$report_file"
        fi
    fi

    cd ..

    if [[ $exit_code -eq 0 ]]; then
        log_success "Node.js linting completed for $service"
    else
        log_error "Node.js linting failed for $service"
    fi

    return $exit_code
}

# Lint single service
lint_service() {
    local service=$1
    local service_dir="plasma-engine-$service"

    log_info "Starting lint for service: $service"

    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        return 1
    fi

    # Determine service type and lint accordingly
    if [[ "$service" == "gateway" ]]; then
        lint_nodejs_service "$service"
    else
        lint_python_service "$service"
    fi
}

# Run linting in parallel
lint_parallel() {
    log_info "Running linting in parallel: ${SERVICES[*]}"

    local pids=()
    local failed_services=()

    # Start linting in background
    for service in "${SERVICES[@]}"; do
        (
            lint_service "$service" 2>&1 | sed "s/^/[$service] /"
            echo $? > "/tmp/lint_${service}_status"
        ) &
        pids+=($!)
    done

    # Wait for all linting to complete
    for i in "${!pids[@]}"; do
        local pid=${pids[i]}
        local service=${SERVICES[i]}

        wait $pid
        local status=$(cat "/tmp/lint_${service}_status" 2>/dev/null || echo "1")

        if [[ $status -ne 0 ]]; then
            failed_services+=("$service")
        fi

        rm -f "/tmp/lint_${service}_status"
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services passed linting in parallel"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Run linting sequentially
lint_sequential() {
    log_info "Running linting sequentially: ${SERVICES[*]}"

    local failed_services=()

    for service in "${SERVICES[@]}"; do
        if ! lint_service "$service"; then
            failed_services+=("$service")
            log_error "Linting failed for service: $service"
        fi
    done

    # Report results
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services passed linting"
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Generate lint summary report
generate_lint_report() {
    local start_time=$1
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [[ "$GENERATE_REPORTS" != true ]]; then
        return 0
    fi

    log_info "Generating lint summary report..."

    local report_file="reports/lint-summary.md"

    cat > "$report_file" << EOF
# Lint Summary Report

**Generated:** $(date)
**Duration:** ${duration}s
**Services:** ${SERVICES[*]}
**Fix Issues:** $FIX_ISSUES
**Strict Mode:** $STRICT_MODE

## Individual Reports
EOF

    # Add links to individual service reports
    for service in "${SERVICES[@]}"; do
        if [[ "$service" == "gateway" ]]; then
            if [[ -f "reports/lint-results/$service-nodejs.txt" ]]; then
                echo "- [$service (Node.js)](lint-results/$service-nodejs.txt)" >> "$report_file"
            fi
        else
            if [[ -f "reports/lint-results/$service-python.txt" ]]; then
                echo "- [$service (Python)](lint-results/$service-python.txt)" >> "$report_file"
            fi
        fi
    done

    cat >> "$report_file" << EOF

## Configuration
- Auto-fix enabled: $FIX_ISSUES
- Strict mode: $STRICT_MODE
- Parallel execution: $PARALLEL_LINT

## Tools Used
### Python Services
- **black**: Code formatting
- **ruff**: Fast Python linter
- **mypy**: Static type checking
- **bandit**: Security linting
- **isort**: Import sorting

### Node.js Services
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **npm audit**: Security vulnerability scanning
EOF

    echo
    echo "============================================"
    echo "           LINT SUMMARY"
    echo "============================================"
    echo "Lint duration: ${duration}s"
    echo "Services linted: ${SERVICES[*]}"
    echo "Fix issues: $FIX_ISSUES"
    echo "Strict mode: $STRICT_MODE"
    echo "Parallel execution: $PARALLEL_LINT"
    echo "Report generated: $report_file"
    echo "============================================"

    log_success "Lint summary report generated: $report_file"
}

# Main function
main() {
    local start_time=$(date +%s)

    # Parse command line arguments
    parse_args "$@"

    # Show configuration if requested
    if [[ "${SHOW_CONFIG:-false}" == true ]]; then
        show_configuration
        exit 0
    fi

    log_info "Starting Plasma Engine lint process"
    log_info "Services to lint: ${SERVICES[*]}"

    # Setup lint environment
    setup_lint_environment

    # Run linting
    if [[ "$PARALLEL_LINT" == true ]]; then
        if ! lint_parallel; then
            log_error "Parallel linting failed"
            exit 1
        fi
    else
        if ! lint_sequential; then
            log_error "Sequential linting failed"
            exit 1
        fi
    fi

    # Generate lint report
    generate_lint_report $start_time

    log_success "Lint process completed successfully!"
}

# Run main function with all arguments
main "$@"