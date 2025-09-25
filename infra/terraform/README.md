/*
Explainer: Organization-level Terraform starter for Plasma Engine.

This directory provides a minimal, provider-agnostic scaffold with version pinning,
inputs/outputs placeholders, and guidance for remote state. It is NOT safe to
apply as-is. Wire credentials, remote state, and modules before any plan/apply.

Structure:
- versions.tf     -> Terraform/core and provider version constraints
- providers.tf    -> Provider configuration placeholders (commented)
- variables.tf    -> Input variables with sensible defaults and type hints
- outputs.tf      -> Output values for downstream stacks and CI
- main.tf         -> Module wiring and stack composition examples

TODOs:
- TODO(infra@plasma): Choose provider(s) and configure authentication.
- TODO(infra@plasma): Configure remote state backend (e.g., S3+Dynamo or GCS).
- TODO(security@plasma): Define least-privileged roles for CI service accounts.
*/

# Terraform Starter

See inline comments in the `.tf` files for detailed guidance.

