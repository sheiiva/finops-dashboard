# AWS Adapter Field Mapping

## Inputs

Adapter accepts:

1. **Already normalized** records with `provider: aws` and all fields in `config/schema/normalized-cost-asset.schema.json` (pass-through).
2. **AWS Cost and Usage Report (CUR)** style rows (flattened columns), including:

| CUR column | Normalized field |
|------------|------------------|
| `line_item_resource_id` | `resource_id` |
| `line_item_line_item_type` | `resource_type` (fallback) |
| `product_servicecode` | `service` |
| `product_region` | `region` |
| `line_item_unblended_cost` | `cost_amount` |
| `line_item_currency_code` | `cost_currency` (3-letter) |
| `line_item_usage_amount` | `usage_quantity` |
| `line_item_usage_type` | `usage_unit` |
| `line_item_usage_start_date` | `timestamp` (RFC3339) |
| `resource_tags_user_*` | `tags` map + `environment` / `owner` when keys match |

## Errors

- Missing timestamp → `ValueError` from `normalize()`.

## Implementation

- `scripts/adapters/aws.py`
- Helpers: `scripts/adapters/normalize_utils.py`
