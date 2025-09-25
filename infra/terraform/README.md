# Terraform Skeleton (Seed)

This directory provides a minimal, well-commented Terraform skeleton that other agents can extend.

- Providers: Default to AWS; switchable once cloud choice is finalized.
- Remote state: S3+DynamoDB backend recommended; configure via `backend.tf`.
- Modules: Basic `network` (VPC + subnets) and `compute` (placeholder SG) to show composition.

## Layout

- `versions.tf`, `providers.tf`, `backend.tf`, `variables.tf` — Root configuration
- `modules/network` — VPC + public subnets
- `modules/compute` — Placeholder compute security group
- `envs/dev` — Wires modules for the dev environment

## Usage

1. Create remote state backend (bucket + dynamodb) — see `scripts/bootstrap-infra.sh`.
2. Initialize and plan in dev:
   ```bash
   cd infra/terraform/envs/dev
   terraform init
   terraform plan -var="aws_region=us-east-1"
   ```
3. Apply once approved via GitHub environment protections.

## TODOs

- Choose cloud provider and finalize provider configuration.
- Add private subnets, NAT GW, route tables in `network`.
- Replace compute placeholder with ECS/EKS per platform decision.