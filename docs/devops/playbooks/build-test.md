# Playbook: Build & Test

Purpose: Standard build and test flow for services.

Inputs:
- Target service path
- Node/Python version (see repo docs)

Outputs:
- Lint/test reports
- Build artifacts (if applicable)

Steps:
1. Install dependencies.
2. Lint and format check.
3. Run unit tests.
4. Build artifacts (when defined).

Commands (examples):
```bash
# Node
npm ci
npm run lint
npm test
npm run build

# Python
pip install -r requirements-dev.txt
ruff check .
black --check .
pytest -q
```

TODO: Add service-specific commands and coverage thresholds.