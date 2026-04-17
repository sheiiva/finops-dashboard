# Contributing Guide

## Workflow

1. Create or pick an issue with clear acceptance criteria.
2. Create a branch from `main` named:
   - `feat/<issue-id>-<slug>`
   - `fix/<issue-id>-<slug>`
   - `docs/<issue-id>-<slug>`
   - `chore/<issue-id>-<slug>`
3. Keep changes scoped to one issue.
4. Open a pull request and link the issue (`Closes #<id>`).
5. Merge with squash after checks pass.

## Commit Standard

Conventional Commits are mandatory.

Examples:
- `feat(collector): add gcp billing export parser`
- `fix(detection): handle missing ownership tags`
- `docs(runbook): define anomaly escalation path`

## Pull Request Standard

- Use the PR template.
- Include objective, scope, test evidence, and rollback notes.
- Update documentation for behavior changes.

## Quality Gates

Pull requests must pass:
- CI quality workflow
- Dependency review
- CodeQL analysis

## Security and Secrets

- Never commit secrets, credentials, or keys.
- Use secret managers and CI secrets only.
- Report vulnerabilities using `SECURITY.md`.
