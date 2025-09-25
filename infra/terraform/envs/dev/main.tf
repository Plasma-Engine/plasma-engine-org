// Explainer: Dev environment entry point. Wires network and compute modules with dev-friendly defaults.
// Inputs: See variables.tf in this env
// Outputs: See outputs.tf in this env
// Downstream: Acts as the target for Terraform plan/apply via CI GitHub environment "dev".

module "network" {
  source      = "../../modules/network"
  name_prefix = var.name_prefix
  cidr_block  = var.cidr_block
  azs         = var.azs
  tags        = var.tags
}

module "compute" {
  source      = "../../modules/compute"
  name_prefix = var.name_prefix
  vpc_id      = module.network.vpc_id
  subnet_ids  = module.network.public_subnet_ids
  tags        = var.tags
}