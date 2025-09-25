output "cluster_name" {
  description = "Kubernetes cluster name."
  value       = var.cluster_name
}

output "cluster_endpoint" {
  description = "API server endpoint URL."
  value       = null
}

output "cluster_ca" {
  description = "Base64 cluster CA data for kubeconfig."
  value       = null
}

