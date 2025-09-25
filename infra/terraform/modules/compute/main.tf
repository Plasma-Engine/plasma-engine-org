/**
  Compute module (provider-agnostic scaffold)

  Purpose: Provision compute workloads (VMs, container services, serverless functions).
  This placeholder allows selecting a provider-specific implementation later.

  References:
  - AWS ECS/EKS: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
  - Azure AKS/VMSS: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
  - GCP GKE/Compute: https://registry.terraform.io/providers/hashicorp/google/latest/docs

  # TODO: Implement compute resources based on chosen runtime (Kubernetes/VM/Serverless).
*/

locals {
  module_purpose = "Provision compute resources and baseline capacity"
}

