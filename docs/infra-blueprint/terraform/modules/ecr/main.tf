# Module: ecr (or equivalent registry)
# Purpose: Create container repositories for each service and configure lifecycle policies.

terraform {
  required_version = ">= 1.5.0"
}

# Suggested repositories: gateway, agent, brand, content, research
# Apply immutability, scan-on-push, and retention policies.

