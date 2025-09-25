# Module: eks
# Purpose: Provision a managed Kubernetes control plane and worker node groups.
# Guidance:
# - Prefer managed node groups with minimal privileged permissions.
# - Enable control-plane logging and cluster audit logs.
# - OIDC provider setup for IRSA (service account roles).
# - Output kubeconfig data and cluster endpoint/CA for consumers (e.g., GitHub Actions).

terraform {
  required_version = ">= 1.5.0"
}

# Sketch (provider-specific resources intentionally omitted):
# - aws_eks_cluster.this
# - aws_eks_node_group.default
# - aws_iam_openid_connect_provider.oidc

