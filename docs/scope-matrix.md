# Scope Matrix

This matrix defines initial coverage for accounts/scopes, regions, and environments used during discovery.

## In Scope

| Platform | Scope ID | Region(s) | Environment(s) | Owner | Notes |
| --- | --- | --- | --- | --- | --- |
| GCP | `billing-account-123` | `europe-west1`, `us-central1` | `dev`, `prod` | `platform-team` | Initial provider baseline for early milestones |
| AWS | `123456789012` | `eu-west-1` | `dev` | `platform-team` | Included for future adapter parity testing |
| Azure | `00000000-0000-0000-0000-000000000000` | `westeurope` | `dev` | `platform-team` | Included for contract validation, not full ingestion yet |

## Out of Scope (Current Phase)

| Scope | Reason |
| --- | --- |
| Additional regions not listed above | Deferred to scaling milestone |
| Non-production legacy accounts with no tagging policy | Requires cleanup policy before onboarding |
| Any scope without owner mapping | Ownership required for accountability and showback/chargeback |

## Ownership Mapping Rules

- Each scoped account/subscription/project must have a named owner group.
- Ownership must map to cost accountability paths used in review cadence.
- Unowned scopes remain out of scope until ownership is established.
