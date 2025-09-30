#!/usr/bin/env python3
"""
Diagnostic and fix script for Python import path issues in Plasma Engine services.
This script helps identify and resolve cross-service import conflicts.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple

class ImportPathFixer:
    """Diagnose and fix Python import path issues in microservices."""

    def __init__(self, service_name: str = "research"):
        self.service_name = service_name
        self.service_dir = Path.cwd()
        self.issues = []
        self.fixes = []

    def diagnose(self) -> Dict:
        """Run diagnostics to identify import path issues."""
        print(f"🔍 Running diagnostics for plasma-engine-{self.service_name}...")

        diagnostics = {
            "service": f"plasma-engine-{self.service_name}",
            "current_dir": str(self.service_dir),
            "python_version": sys.version,
            "python_path": sys.path[:],
            "pythonpath_env": os.environ.get("PYTHONPATH", ""),
            "issues": [],
            "recommendations": []
        }

        # Check 1: PYTHONPATH environment variable
        if os.environ.get("PYTHONPATH"):
            paths = os.environ["PYTHONPATH"].split(":")
            for path in paths:
                if "plasma-engine" in path and self.service_name not in path:
                    diagnostics["issues"].append({
                        "type": "PYTHONPATH_CONFLICT",
                        "description": f"PYTHONPATH contains other service directory: {path}",
                        "severity": "HIGH"
                    })

        # Check 2: Check for duplicate 'app' modules in sys.path
        app_locations = []
        for path in sys.path:
            app_path = Path(path) / "app"
            if app_path.exists() and app_path.is_dir():
                app_locations.append(str(app_path))

        if len(app_locations) > 1:
            diagnostics["issues"].append({
                "type": "MULTIPLE_APP_MODULES",
                "description": f"Multiple 'app' modules found in Python path: {app_locations}",
                "severity": "CRITICAL"
            })

        # Check 3: Check for __init__.py in app directory
        app_init = self.service_dir / "app" / "__init__.py"
        if not app_init.exists():
            diagnostics["issues"].append({
                "type": "MISSING_INIT",
                "description": "Missing __init__.py in app directory",
                "severity": "MEDIUM"
            })

        # Check 4: Check routers module structure
        routers_dir = self.service_dir / "app" / "routers"
        if routers_dir.exists():
            routers_init = routers_dir / "__init__.py"
            if not routers_init.exists():
                diagnostics["issues"].append({
                    "type": "MISSING_ROUTERS_INIT",
                    "description": "Missing __init__.py in app/routers directory",
                    "severity": "HIGH"
                })
            else:
                # Check what's being imported/exported from routers __init__.py
                with open(routers_init, 'r') as f:
                    content = f.read()
                    if "documents" in content and self.service_name == "research":
                        diagnostics["issues"].append({
                            "type": "WRONG_IMPORT",
                            "description": "routers/__init__.py contains 'documents' import (from content service?)",
                            "severity": "CRITICAL"
                        })

        # Generate recommendations based on issues
        if diagnostics["issues"]:
            diagnostics["recommendations"] = self._generate_recommendations(diagnostics["issues"])

        return diagnostics

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate fix recommendations based on identified issues."""
        recommendations = []

        for issue in issues:
            if issue["type"] == "PYTHONPATH_CONFLICT":
                recommendations.append("Clear PYTHONPATH or ensure it only contains current service directory")
            elif issue["type"] == "MULTIPLE_APP_MODULES":
                recommendations.append("Isolate service execution to prevent cross-service imports")
            elif issue["type"] == "MISSING_INIT":
                recommendations.append("Create __init__.py file in app directory")
            elif issue["type"] == "MISSING_ROUTERS_INIT":
                recommendations.append("Create proper __init__.py file in app/routers directory")
            elif issue["type"] == "WRONG_IMPORT":
                recommendations.append("Fix imports in routers/__init__.py to match current service")

        return recommendations

    def fix_imports(self) -> bool:
        """Apply fixes for identified issues."""
        print("\n🔧 Applying fixes...")
        success = True

        # Fix 1: Create __init__.py files if missing
        app_init = self.service_dir / "app" / "__init__.py"
        if not app_init.exists():
            app_init.touch()
            print(f"✅ Created {app_init}")

        routers_dir = self.service_dir / "app" / "routers"
        if routers_dir.exists():
            routers_init = routers_dir / "__init__.py"
            if not routers_init.exists():
                # Create appropriate __init__.py based on service
                self._create_routers_init(routers_init)
                print(f"✅ Created {routers_init}")

        # Fix 2: Create launch script with isolated Python path
        self._create_launch_script()

        # Fix 3: Create .env file with proper configuration
        self._create_env_file()

        return success

    def _create_routers_init(self, init_file: Path):
        """Create appropriate __init__.py for routers based on service."""
        content = '''"""
Router module for plasma-engine-{service}.
This module exports all routers for the {service} service.
"""

from fastapi import APIRouter

# Import routers based on what exists in this directory
import os
from pathlib import Path

router = APIRouter()

# Dynamically import router modules
current_dir = Path(__file__).parent
for file in current_dir.glob("*.py"):
    if file.name != "__init__.py" and not file.name.startswith("_"):
        module_name = file.stem
        # Import each router module dynamically
        try:
            exec(f"from .{{module_name}} import router as {{module_name}}_router")
            exec(f"router.include_router({{module_name}}_router, prefix='/{{module_name}}', tags=['{{module_name}}'])")
            print(f"Loaded router: {{module_name}}")
        except ImportError as e:
            print(f"Could not import router {{module_name}}: {{e}}")

__all__ = ["router"]
'''.format(service=self.service_name)

        with open(init_file, 'w') as f:
            f.write(content)

    def _create_launch_script(self):
        """Create a launch script with proper Python path isolation."""
        script_path = self.service_dir / "launch.sh"

        content = f'''#!/bin/bash
# Launch script for plasma-engine-{self.service_name} with isolated Python path

# Clear any existing PYTHONPATH to prevent cross-service imports
unset PYTHONPATH

# Set the working directory to the service root
cd "$(dirname "$0")"

# Export the service directory as PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Launch the service with uvicorn
echo "Starting plasma-engine-{self.service_name} with isolated Python path..."
echo "PYTHONPATH: $PYTHONPATH"
echo "Working directory: $(pwd)"

python3.11 -m uvicorn app.main:app --port 8000 --reload
'''

        with open(script_path, 'w') as f:
            f.write(content)

        # Make script executable
        os.chmod(script_path, 0o755)
        print(f"✅ Created launch script: {script_path}")

    def _create_env_file(self):
        """Create .env file with proper Python configuration."""
        env_path = self.service_dir / ".env"

        if not env_path.exists():
            content = f'''# Environment configuration for plasma-engine-{self.service_name}

# Python configuration
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1

# Service configuration
SERVICE_NAME=plasma-engine-{self.service_name}
SERVICE_PORT=8000

# Prevent Python from adding parent directory to path
PYTHONNOUSERSITE=1
'''

            with open(env_path, 'w') as f:
                f.write(content)

            print(f"✅ Created .env file: {env_path}")

    def create_test_script(self):
        """Create a test script to verify imports are working."""
        test_path = self.service_dir / "test_imports.py"

        content = '''#!/usr/bin/env python3
"""Test script to verify import paths are correctly configured."""

import sys
import os
from pathlib import Path

print("=" * 60)
print("Import Path Test for Plasma Engine Service")
print("=" * 60)

print(f"\\nPython version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PYTHONPATH env: {os.environ.get('PYTHONPATH', 'Not set')}")

print("\\nPython sys.path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\\nTrying to import app modules...")
try:
    import app
    print("✅ Successfully imported 'app' module")
    print(f"   Location: {app.__file__ if hasattr(app, '__file__') else 'No __file__ attribute'}")
except ImportError as e:
    print(f"❌ Failed to import 'app': {e}")

try:
    from app import main
    print("✅ Successfully imported 'app.main'")
except ImportError as e:
    print(f"❌ Failed to import 'app.main': {e}")

try:
    from app import routers
    print("✅ Successfully imported 'app.routers'")

    # Check what's available in routers
    if hasattr(routers, '__all__'):
        print(f"   Exports: {routers.__all__}")
except ImportError as e:
    print(f"❌ Failed to import 'app.routers': {e}")

print("\\n" + "=" * 60)
print("Test complete!")
'''

        with open(test_path, 'w') as f:
            f.write(content)

        os.chmod(test_path, 0o755)
        print(f"✅ Created test script: {test_path}")

def main():
    """Main function to run diagnostics and fixes."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Python import issues in Plasma Engine services")
    parser.add_argument("--service", default="research", help="Service name (research, content, brand, etc.)")
    parser.add_argument("--fix", action="store_true", help="Apply fixes automatically")
    parser.add_argument("--test", action="store_true", help="Create and run test script")

    args = parser.parse_args()

    fixer = ImportPathFixer(args.service)

    # Run diagnostics
    diagnostics = fixer.diagnose()

    print("\n📊 Diagnostic Results:")
    print(json.dumps(diagnostics, indent=2))

    # Apply fixes if requested
    if args.fix:
        if diagnostics["issues"]:
            fixer.fix_imports()
            print("\n✅ Fixes applied!")
            print("\n📝 Next steps:")
            print("1. Use ./launch.sh to start the service with isolated Python path")
            print("2. Or source .env and run: python3.11 -m uvicorn app.main:app --port 8000")
            print("3. Run with --test flag to verify imports are working")
        else:
            print("\n✅ No issues found!")

    # Create test script if requested
    if args.test:
        fixer.create_test_script()
        print("\n🧪 Running import test...")
        subprocess.run([sys.executable, "test_imports.py"])

    if not args.fix and diagnostics["issues"]:
        print("\n💡 Run with --fix flag to apply fixes automatically")

if __name__ == "__main__":
    main()