# Module: postgres
# Purpose: Provision a managed Postgres database (e.g., AWS RDS, Cloud SQL, Azure Database for PostgreSQL).
# Guidance:
# - Use separate DBs or schemas per service where appropriate.
# - Enforce TLS in-transit and encryption at rest.
# - Parameter group tuned for connection pooling (consider pgbouncer at app layer if needed).

terraform {
  required_version = ">= 1.5.0"
}

# Provider-specific resources intentionally omitted.

