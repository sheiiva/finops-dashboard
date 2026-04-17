# Mandatory Tagging Policy and Compliance Rules

This policy defines required metadata tags for cost allocation and accountability.

## Required Tags

| Tag Key | Purpose | Required |
| --- | --- | --- |
| `owner` | Team or squad accountable for spend | Yes |
| `environment` | Deployment context (`dev`, `stage`, `prod`) | Yes |
| `service` | Service/application identifier | Yes |
| `cost_center` | Financial mapping key for showback/chargeback | Yes |

## Compliance Definition

Compliance score is calculated as:

`compliant_resources / total_resources_in_scope * 100`

Resource is compliant when all required tags exist and values are non-empty.

## Thresholds

- Target compliance: >= 95%
- Warning threshold: < 95%
- Critical threshold: < 90%

## Exception Workflow

1. Exception request filed with justification and owner.
2. Temporary waiver approved with expiry date.
3. Waived resources are tracked separately in compliance reporting.
4. Expired waivers are auto-escalated in weekly FinOps review.
