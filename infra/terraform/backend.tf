// Explainer: Defines the remote backend for Terraform state (S3+DynamoDB recommended on AWS).
// Inputs: Environment variables or TF variables for bucket/table names (set via CI environment).
// Outputs: n/a
// Downstream: Enables team-safe state storage and locking.
// Docs: https://developer.hashicorp.com/terraform/language/settings/backends/s3

terraform {
  backend "s3" {
    // TODO: Owner=DevOps: Create these via bootstrap script and/or manually first time.
    // bucket         = "plasma-engine-terraform-state"
    // key            = "envs/dev/terraform.tfstate"
    // region         = "us-east-1"
    // dynamodb_table = "plasma-engine-terraform-locks"
    // encrypt        = true
  }
}