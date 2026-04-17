# ADR 0001: Template-First Architecture

## Status

Accepted

## Context

The repository is intended for portfolio demonstration and real client reuse, not a single-company deployment.

## Decision

Adopt a template-first architecture:
- Provider-agnostic core for normalized model, rules, scoring, and governance
- Provider-specific adapters for GCP/AWS/Azure ingestion
- Configuration-driven onboarding per organization/environment

## Alternatives Considered

1. Single-cloud first without adapters
2. Full custom implementation per client

## Consequences

- Higher upfront design effort
- Stronger long-term reuse and cleaner multi-cloud extension
- Better interview signal for architecture maturity
