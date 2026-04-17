# Provider Adapter Contract

This document defines the provider adapter interface contract used by cloud-specific collectors.

## Intent

- Keep core FinOps logic provider-agnostic.
- Isolate provider API differences in dedicated adapters.
- Enforce a normalized output contract for downstream rules and dashboards.

## Adapter Responsibilities

Each provider adapter must:

1. Collect inventory metadata.
2. Collect utilization signals.
3. Collect cost records.
4. Normalize outputs to shared record formats.
5. Return structured errors without crashing the full pipeline.

## Required Methods

- `fetch_inventory(scope: dict) -> list[dict]`
- `fetch_utilization(scope: dict) -> list[dict]`
- `fetch_costs(scope: dict) -> list[dict]`
- `normalize(records: list[dict]) -> list[dict]`
- `healthcheck() -> dict`

## Normalized Record Fields (minimum)

- `provider` (`gcp` | `aws` | `azure`)
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

## Error Model

Adapter errors should include:

- `provider`
- `stage` (`inventory|utilization|cost|normalize|healthcheck`)
- `code`
- `message`
- `retryable` (`true|false`)

## Notes

- This contract is intentionally minimal for bootstrap phase.
- Expand fields and strict typing in later milestones once real provider ingestion starts.
