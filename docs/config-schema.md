# Configuration Schema

This document defines the reusable baseline configuration contract for project onboarding.

## Files

- Schema: `config/schema/project-config.schema.json`
- Example: `config/examples/project-config.example.json`
- Validator: `scripts/validate_project_config.py`

## Required top-level fields

- `organization` (string)
- `environment` (string)
- `provider` (`gcp` | `aws` | `azure` | `multi`)
- `billing_scope` (string)
- `tag_policy` (object)

## `tag_policy` fields

- `required_tags` (non-empty string array)
- `enforcement_mode` (`audit` | `enforce`)

## Validation command

```bash
python scripts/validate_project_config.py config/examples/project-config.example.json
```

Expected output:

- `OK: ... passed validation`

## Notes

- This is a bootstrap schema for early implementation phases.
- Extend the schema incrementally in milestone-linked issues to avoid uncontrolled config sprawl.
