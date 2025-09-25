# Bubble up selected outputs for quick discovery

output "cluster_name" {
  description = "Cluster name (if created)."
  value       = try(module.eks[0].cluster_name, null)
}

output "grafana_url" {
  description = "Grafana URL (if exposed)."
  value       = try(module.observability[0].grafana_url, null)
}

