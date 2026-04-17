# CI Gates

## Required checks on `main`

| Workflow | Gate |
|----------|------|
| `ci-quality.yml` | Repo files present; **Ruff** lint on `scripts/` and `tests/`; **pytest**; YAML/markdown hooks optional locally |
| `terraform-validate.yml` | Terraform fmt/validate on tracked `.tf` |
| `codeql.yml` | CodeQL analysis (Python) |
| `dependency-review.yml` | Dependency review on PRs |

## Failure criteria

- Any required job **red** → PR not merge-ready (branch protection).  
- **Ruff** or **pytest** failure → fix code or tests; no bypass on `main`.  
- **Terraform** validate failure → fix module or workflow scope.

## Security scans

- CodeQL for static analysis.  
- GitGuardian (if enabled on repo).  
- Dependabot for Actions (see `.github/dependabot.yml`).

## Local parity

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m ruff check scripts tests
python3 -m pytest
```
