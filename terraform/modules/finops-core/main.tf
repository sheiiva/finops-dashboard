locals {
  module_context = {
    name_prefix = var.name_prefix
    environment = var.environment
    tags        = var.tags
  }
}

# Module scaffold intentionally contains no resources yet.
# Resource composition is implemented incrementally via follow-up milestone issues.
