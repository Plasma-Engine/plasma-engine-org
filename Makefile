# Plasma Engine Organization Makefile
# Manages all repositories and services

.PHONY: help
help: ## Show this help message
	@echo "Plasma Engine Organization Management"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Repository Management
.PHONY: clone-all
clone-all: ## Clone all Plasma Engine repositories
	@echo "Cloning all repositories..."
	@for repo in gateway research brand content agent shared infra; do \
		if [ ! -d "plasma-engine-$$repo" ]; then \
			git clone https://github.com/plasma-engine/plasma-engine-$$repo.git; \
		else \
			echo "plasma-engine-$$repo already exists"; \
		fi \
	done

.PHONY: pull-all
pull-all: ## Pull latest changes for all repositories
	@echo "Pulling latest changes..."
	@for repo in gateway research brand content agent shared infra; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "Updating plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && git pull && cd ..; \
		fi \
	done

.PHONY: status-all
status-all: ## Show git status for all repositories
	@echo "Repository Status:"
	@for repo in gateway research brand content agent shared infra; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "\n📁 plasma-engine-$$repo:"; \
			cd plasma-engine-$$repo && git status -sb && cd ..; \
		fi \
	done

# Development Environment
.PHONY: setup
setup: ## Complete setup of development environment
	@echo "Setting up development environment..."
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh setup

.PHONY: install-deps
install-deps: ## Install dependencies for all services
	@echo "Installing dependencies..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "Installing deps for plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && \
			if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi && \
			if [ -f "package.json" ]; then npm install; fi && \
			cd ..; \
		fi \
	done

.PHONY: init-db
init-db: ## Initialize all databases
	@echo "Initializing databases..."
	cd plasma-engine-infra && docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_engine;"
	cd plasma-engine-infra && docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_research;"
	cd plasma-engine-infra && docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_brand;"
	cd plasma-engine-infra && docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_content;"
	cd plasma-engine-infra && docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_agent;"

# Docker Compose Commands
.PHONY: up
up: ## Start all services with Docker Compose
	docker-compose up -d

.PHONY: down
down: ## Stop all services
	docker-compose down

.PHONY: restart
restart: down up ## Restart all services

.PHONY: ps
ps: ## Show running services
	docker-compose ps

.PHONY: health
health: ## Check service health status
	@./scripts/dev.sh status

.PHONY: up-minimal
up-minimal: ## Start only core services (faster startup)
	docker-compose up -d postgres redis gateway

# Service Management
.PHONY: start-infra
start-infra: ## Start infrastructure services
	docker-compose up -d postgres redis neo4j rabbitmq

.PHONY: stop-infra
stop-infra: ## Stop infrastructure services
	docker-compose stop postgres redis neo4j rabbitmq

.PHONY: run-gateway
run-gateway: ## Run Gateway service
	cd plasma-engine-gateway && npm run dev

.PHONY: run-research
run-research: ## Run Research service
	cd plasma-engine-research && uvicorn app.main:app --reload

.PHONY: run-brand
run-brand: ## Run Brand service
	cd plasma-engine-brand && uvicorn app.main:app --reload --port 8001

.PHONY: run-content
run-content: ## Run Content service
	cd plasma-engine-content && uvicorn app.main:app --reload --port 8002

.PHONY: run-agent
run-agent: ## Run Agent service
	cd plasma-engine-agent && uvicorn app.main:app --reload --port 8003

.PHONY: run-all
run-all: start-infra ## Run all services
	@echo "Starting all services..."
	@tmux new-session -d -s plasma-engine
	@tmux send-keys -t plasma-engine "cd plasma-engine-gateway && npm run dev" Enter
	@tmux split-window -t plasma-engine -h
	@tmux send-keys -t plasma-engine "cd plasma-engine-research && uvicorn app.main:app --reload" Enter
	@tmux split-window -t plasma-engine -v
	@tmux send-keys -t plasma-engine "cd plasma-engine-brand && uvicorn app.main:app --reload --port 8001" Enter
	@tmux select-pane -t plasma-engine -L
	@tmux split-window -t plasma-engine -v
	@tmux send-keys -t plasma-engine "cd plasma-engine-content && uvicorn app.main:app --reload --port 8002" Enter
	@tmux new-window -t plasma-engine
	@tmux send-keys -t plasma-engine "cd plasma-engine-agent && uvicorn app.main:app --reload --port 8003" Enter
	@tmux attach -t plasma-engine

# Testing
.PHONY: test-all
test-all: ## Run tests for all services
	@echo "Running tests..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "\n🧪 Testing plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && \
			if [ -f "pytest.ini" ]; then pytest; fi && \
			if [ -f "package.json" ] && grep -q "\"test\"" package.json; then npm test; fi && \
			cd ..; \
		fi \
	done

.PHONY: lint-all
lint-all: ## Run linting for all services
	@echo "Running linters..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "\n🔍 Linting plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && \
			if [ -f ".flake8" ] || [ -f "setup.cfg" ]; then flake8; fi && \
			if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ]; then npm run lint; fi && \
			cd ..; \
		fi \
	done

# Docker Management
.PHONY: build-all
build-all: ## Build Docker images for all services
	@echo "Building Docker images..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ] && [ -f "plasma-engine-$$repo/Dockerfile" ]; then \
			echo "Building plasma-engine-$$repo..."; \
			docker build -t plasma-engine/$$repo:latest plasma-engine-$$repo; \
		fi \
	done

.PHONY: push-all
push-all: ## Push Docker images to registry
	@echo "Pushing Docker images..."
	@for repo in gateway research brand content agent; do \
		docker push plasma-engine/$$repo:latest; \
	done

# Database Commands
.PHONY: db-migrate
db-migrate: ## Run database migrations
	@./scripts/dev.sh migrate

.PHONY: db-reset
db-reset: ## Reset all databases (WARNING: destroys data)
	@./scripts/dev.sh reset-db

.PHONY: db-seed
db-seed: ## Load seed data
	docker-compose exec -T postgres psql -U plasma < scripts/db/init/02-seed-data.sql

.PHONY: db-backup
db-backup: ## Backup all databases
	@mkdir -p backups
	docker-compose exec postgres pg_dumpall -U plasma > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/"

.PHONY: db-restore
db-restore: ## Restore database from latest backup
	@latest=$$(ls -t backups/*.sql | head -1); \
	if [ -z "$$latest" ]; then \
		echo "❌ No backup found"; \
		exit 1; \
	fi; \
	echo "Restoring from $$latest..."; \
	docker-compose exec -T postgres psql -U plasma < $$latest

# Shell Access
.PHONY: shell-gateway
shell-gateway: ## Open Python shell in gateway service
	docker-compose exec gateway python

.PHONY: shell-postgres
shell-postgres: ## Open PostgreSQL CLI
	docker-compose exec postgres psql -U plasma -d plasma_engine

.PHONY: shell-redis
shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

# Utilities
.PHONY: clean
clean: ## Clean all build artifacts and dependencies
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: logs
logs: ## Show logs for all services
	docker-compose logs -f --tail=100

.PHONY: logs-gateway
logs-gateway: ## Show gateway logs
	docker-compose logs -f --tail=100 gateway

.PHONY: urls
urls: ## Show all service URLs and credentials
	@./scripts/dev.sh urls

.PHONY: sync-templates
sync-templates: ## Sync templates across repositories
	cd plasma-engine-shared && ./scripts/sync-templates.sh

.PHONY: update-deps
update-deps: ## Update dependencies for all services
	@echo "Updating dependencies..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "Updating plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && \
			if [ -f "requirements.txt" ]; then pip-compile --upgrade; fi && \
			if [ -f "package.json" ]; then npm update; fi && \
			cd ..; \
		fi \
	done

# Documentation
.PHONY: docs
docs: ## Generate documentation
	@echo "Generating documentation..."
	@for repo in gateway research brand content agent; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			echo "Documenting plasma-engine-$$repo..."; \
			cd plasma-engine-$$repo && \
			if [ -f "mkdocs.yml" ]; then mkdocs build; fi && \
			cd ..; \
		fi \
	done

.PHONY: serve-docs
serve-docs: ## Serve documentation locally
	cd docs && python -m http.server 8080

# Release Management
.PHONY: version
version: ## Show version for all services
	@echo "Service Versions:"
	@for repo in gateway research brand content agent shared infra; do \
		if [ -d "plasma-engine-$$repo" ] && [ -f "plasma-engine-$$repo/package.json" ]; then \
			version=$$(cd plasma-engine-$$repo && node -p "require('./package.json').version" 2>/dev/null || echo "N/A"); \
			echo "plasma-engine-$$repo: $$version"; \
		elif [ -d "plasma-engine-$$repo" ] && [ -f "plasma-engine-$$repo/pyproject.toml" ]; then \
			version=$$(cd plasma-engine-$$repo && grep version pyproject.toml | head -1 | cut -d'"' -f2 2>/dev/null || echo "N/A"); \
			echo "plasma-engine-$$repo: $$version"; \
		fi \
	done

.PHONY: tag-release
tag-release: ## Tag a new release
	@read -p "Enter version (e.g., v1.0.0): " version; \
	for repo in gateway research brand content agent shared infra; do \
		if [ -d "plasma-engine-$$repo" ]; then \
			cd plasma-engine-$$repo && \
			git tag $$version && \
			git push origin $$version && \
			cd ..; \
		fi \
	done

# Default target
.DEFAULT_GOAL := help
