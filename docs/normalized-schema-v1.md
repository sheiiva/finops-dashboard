# Normalized Cost and Asset Schema v1

This schema defines the canonical record format used by provider collectors.

## Files

- Schema: `config/schema/normalized-cost-asset.schema.json`
- Example: `config/examples/normalized-cost-asset.example.json`

## Goals

- Standardize provider outputs for downstream rules and dashboards.
- Ensure core fields required for allocation and prioritization are always present.
- Keep versioned contract stable across adapters.

## Required Fields

- `provider`
- `resource_id`
- `resource_type`
- `environment`
- `owner`
- `service`
- `region`
- `cost_amount`
- `cost_currency`
- `usage_quantity`
- `usage_unit`
- `timestamp`

## Versioning Rules

- Breaking field changes require schema version bump.
- New optional fields can be introduced in minor updates.
- Adapter outputs must remain backward-compatible with v1 consumers.
