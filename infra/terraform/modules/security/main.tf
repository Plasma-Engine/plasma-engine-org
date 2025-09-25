/**
  Security module (provider-agnostic scaffold)

  Purpose: Security baselines: KMS keys, secrets backends, vulnerability scanning hooks.

  # TODO: Integrate with chosen secrets manager and KMS provider.
*/

locals {
  module_purpose = "Provision security primitives and policies"
}

