# finops-core module

Reusable base module scaffold for FinOps platform infrastructure.

## Purpose

- Standardize baseline module interface (`name_prefix`, `environment`, `tags`)
- Provide multi-cloud provider version constraints for future resource composition
- Enable incremental implementation through milestone-linked issues

## Usage

```hcl
module "finops_core" {
  source      = "./modules/finops-core"
  name_prefix = "finops"
  environment = "dev"
  tags = {
    owner       = "platform"
    environment = "dev"
  }
}
```

## Current scope

Scaffold only. No resources are created yet.
