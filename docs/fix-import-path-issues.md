# Fix for Python Import Path Issues in Plasma Engine Services

## Problem Description

The research service (and potentially other services) fail to start due to Python import path resolution issues. The error manifests as:

```
ImportError: cannot import name 'documents' from 'app.routers' (/Users/.../plasma-engine-content/app/routers/__init__.py)
```

This indicates Python is importing from the wrong service directory (content instead of research).

## Root Causes

1. **PYTHONPATH Pollution**: Multiple service directories in PYTHONPATH causing cross-service imports
2. **Namespace Collisions**: All services use `app` as the root module, causing conflicts
3. **Module Resolution Order**: Python's import system finding modules from wrong service first
4. **Missing Isolation**: Services not properly isolated during development

## Quick Fix

### For plasma-engine-research (or any affected service):

1. **Navigate to the service directory:**
   ```bash
   cd plasma-engine-research
   ```

2. **Run the fix script:**
   ```bash
   # Copy the fix script from the org repo
   cp ../plasma-engine-org/scripts/fix-python-imports.py .

   # Run diagnostics
   python3 fix-python-imports.py --service research

   # Apply fixes
   python3 fix-python-imports.py --service research --fix

   # Test the fixes
   python3 fix-python-imports.py --service research --test
   ```

3. **Start the service using the new launch script:**
   ```bash
   ./launch.sh
   ```

## Manual Fix Steps

If you prefer to fix manually:

### 1. Clear PYTHONPATH

```bash
unset PYTHONPATH
```

### 2. Create proper `__init__.py` files

```bash
# In plasma-engine-research directory
touch app/__init__.py
touch app/routers/__init__.py
```

### 3. Fix routers/__init__.py

Create/update `app/routers/__init__.py` with service-specific imports:

```python
"""Router module for plasma-engine-research."""

from fastapi import APIRouter

router = APIRouter()

# Import only research-specific routers
# Do NOT import from other services

__all__ = ["router"]
```

### 4. Launch with isolated Python path

```bash
# From plasma-engine-research directory
cd plasma-engine-research
export PYTHONPATH="$(pwd)"
python3.11 -m uvicorn app.main:app --port 8000
```

## Prevention

### Best Practices for Development

1. **Use Virtual Environments**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Never set global PYTHONPATH**
   - Remove any PYTHONPATH exports from ~/.bashrc or ~/.zshrc
   - Use project-specific environment variables

3. **Use Docker for isolation**
   ```bash
   # Each service should have its own container
   docker-compose up plasma-engine-research
   ```

4. **Unique module names**
   - Consider renaming `app` to service-specific names:
     - `research_app` for plasma-engine-research
     - `content_app` for plasma-engine-content
     - etc.

## Service-Specific Fixes

### For All Services

Run the fix script for each service:

```bash
# Research Service
cd plasma-engine-research
python3 ../plasma-engine-org/scripts/fix-python-imports.py --service research --fix

# Content Service
cd ../plasma-engine-content
python3 ../plasma-engine-org/scripts/fix-python-imports.py --service content --fix

# Brand Service
cd ../plasma-engine-brand
python3 ../plasma-engine-org/scripts/fix-python-imports.py --service brand --fix

# Agent Service
cd ../plasma-engine-agent
python3 ../plasma-engine-org/scripts/fix-python-imports.py --service agent --fix
```

## Verification

After applying fixes, verify each service:

```bash
# Test imports
python3 test_imports.py

# Start service
./launch.sh

# Check health endpoint
curl http://localhost:8000/health
```

## Long-term Solution

Consider implementing these architectural changes:

1. **Rename app modules** to unique names per service
2. **Use Docker Compose** for local development
3. **Implement proper CI/CD** with isolated test environments
4. **Use package management** with namespace packages

## Troubleshooting

If issues persist:

1. **Check for hardcoded paths:**
   ```bash
   grep -r "plasma-engine-content" .
   grep -r "PYTHONPATH" .
   ```

2. **Clean Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   ```

3. **Verify Python version:**
   ```bash
   python3.11 --version
   which python3.11
   ```

4. **Check for stale imports:**
   ```bash
   python3.11 -c "import sys; print('\n'.join(sys.path))"
   ```

## Emergency Workaround

If you need to start the service immediately:

```bash
# Create a temporary isolated directory
mkdir /tmp/plasma-research-isolated
cp -r plasma-engine-research/* /tmp/plasma-research-isolated/
cd /tmp/plasma-research-isolated
unset PYTHONPATH
python3.11 -m uvicorn app.main:app --port 8000
```

This creates a completely isolated copy away from any other services.