"""Automation script helpers and orchestration entry points.

The `automation` package groups Python utilities that GitHub Actions and
background agents execute to coordinate Cursor specialists, CodeRabbit
reviews, and downstream DevOps workflows. Every module inside this package
follows the repository guideline of embedding rich commentary so future
automation engineers can hand the system off without tribal knowledge.

Keeping the package explicit also enables intra-package imports (for example,
the autopilot orchestrator reuses Cursor dispatch utilities) while avoiding
implicit namespace collisions should additional helper modules be added later
on.
"""


