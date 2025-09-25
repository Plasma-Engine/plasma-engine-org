#!/usr/bin/env bash
# Explainer: Bootstraps Terraform remote state backend on AWS (S3 + DynamoDB).
# Purpose: Create idempotent, minimal primitives required before any terraform init.
# Inputs:
#   - AWS_REGION (env) — e.g., us-east-1
#   - TF_STATE_BUCKET (env) — e.g., plasma-engine-terraform-state
#   - TF_LOCK_TABLE (env) — e.g., plasma-engine-terraform-locks
# Outputs:
#   - S3 bucket for state; DynamoDB table for state locks.
# Downstream: Consumed by terraform backend in infra/terraform/backend.tf
# Docs: https://developer.hashicorp.com/terraform/language/settings/backends/s3
# TODO: Owner=DevOps: Prefer using Rube MCP wrappers for AWS calls when available.
set -euo pipefail

AWS_REGION=${AWS_REGION:-"us-east-1"}
TF_STATE_BUCKET=${TF_STATE_BUCKET:-"plasma-engine-terraform-state"}
TF_LOCK_TABLE=${TF_LOCK_TABLE:-"plasma-engine-terraform-locks"}

echo "[bootstrap-infra] Using region=${AWS_REGION} bucket=${TF_STATE_BUCKET} table=${TF_LOCK_TABLE}"

# Check AWS CLI presence
if ! command -v aws >/dev/null 2>&1; then
  echo "ERROR: aws CLI not found. Install AWS CLI v2 and configure credentials." >&2
  exit 1
fi

# Create S3 bucket if not exists
if aws s3api head-bucket --bucket "${TF_STATE_BUCKET}" >/dev/null 2>&1; then
  echo "S3 bucket exists: ${TF_STATE_BUCKET}"
else
  echo "Creating S3 bucket: ${TF_STATE_BUCKET}"
  aws s3api create-bucket \
    --bucket "${TF_STATE_BUCKET}" \
    --region "${AWS_REGION}" \
    $( [ "${AWS_REGION}" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=${AWS_REGION}" )

  echo "Enabling default encryption and versioning on ${TF_STATE_BUCKET}"
  aws s3api put-bucket-encryption --bucket "${TF_STATE_BUCKET}" --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
  aws s3api put-bucket-versioning --bucket "${TF_STATE_BUCKET}" --versioning-configuration Status=Enabled
fi

# Create DynamoDB table if not exists
if aws dynamodb describe-table --table-name "${TF_LOCK_TABLE}" >/dev/null 2>&1; then
  echo "DynamoDB table exists: ${TF_LOCK_TABLE}"
else
  echo "Creating DynamoDB table: ${TF_LOCK_TABLE}"
  aws dynamodb create-table \
    --table-name "${TF_LOCK_TABLE}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "${AWS_REGION}"
  echo "Waiting for table to become ACTIVE..."
  aws dynamodb wait table-exists --table-name "${TF_LOCK_TABLE}" --region "${AWS_REGION}"
fi

echo "[bootstrap-infra] Done. Configure backend.tf with bucket=${TF_STATE_BUCKET} table=${TF_LOCK_TABLE}."