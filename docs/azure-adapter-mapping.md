# Azure Adapter Field Mapping

## Inputs

1. **Normalized** records with `provider: azure` and full schema fields (pass-through).
2. **Azure Cost Management** style export rows (common column names):

| Export column | Normalized field |
|---------------|------------------|
| `ResourceId` | `resource_id` |
| `ResourceType` | `resource_type` |
| `ServiceName` | `service` |
| `ResourceLocation` | `region` |
| `CostInBillingCurrency` | `cost_amount` |
| `BillingCurrencyCode` | `cost_currency` |
| `ConsumedQuantity` | `usage_quantity` (default `1` if absent) |
| `UnitOfMeasure` | `usage_unit` |
| `UsageDate` | `timestamp` |
| `tags` object or JSON `Tags` string | `tags` + `environment` / `owner` |

## Errors

- Missing `UsageDate` / `Date` / `timestamp` → `ValueError`.

## Implementation

- `scripts/adapters/azure.py`
