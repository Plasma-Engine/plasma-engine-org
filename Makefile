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
setup: clone-all ## Complete setup of development environment
	@echo "Setting up development environment..."
	cd plasma-engine-infra && docker-compose up -d
	@echo "Installing dependencies..."
	$(MAKE) install-deps
	@echo "Initializing databases..."
	$(MAKE) init-db
	@echo "✅ Setup complete!"

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

# Service Management
.PHONY: start-infra
start-infra: ## Start infrastructure services
	cd plasma-engine-infra && docker-compose up -d

.PHONY: stop-infra
stop-infra: ## Stop infrastructure services
	cd plasma-engine-infra && docker-compose down

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

.PHONY: onboard
onboard: ## Developer onboarding helper
	./scripts/dev-onboard.sh

.PHONY: validate
validate: ## Run local validation (formatters/linters/tests placeholders)
	./scripts/dev-local-validate.sh

.PHONY: deploy-scripts
deploy-scripts: ## Use scripts/deploy.sh to orchestrate deployment (placeholder)
	./scripts/deploy.sh $(env)

.PHONY: logs
logs: ## Show logs for all services
	cd plasma-engine-infra && docker-compose logs -f

.PHONY: ps
ps: ## Show running services
	cd plasma-engine-infra && docker-compose ps

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
