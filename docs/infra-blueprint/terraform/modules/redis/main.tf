# Module: redis
# Purpose: Provision a managed Redis (e.g., ElastiCache) for caching and queues (if applicable).
# Guidance:
# - Enable encryption in-transit and at-rest.
# - Place within private subnets; restrict access to application SGs.

terraform {
  required_version = ">= 1.5.0"
}

