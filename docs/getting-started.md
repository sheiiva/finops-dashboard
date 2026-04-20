# Getting Started

## Prerequisites

- Git
- Python 3.11+
- Terraform 1.6+
- Pre-commit
- Docker (optional for local tooling)

## 1) Clone

```bash
git clone git@github.com:sheiiva/finops-dashboard.git
cd finops-dashboard
```

## 2) Configure environment

```bash
cp .env.example .env
```

Populate values in `.env` for your test scope. Do not commit `.env`.

## 3) Install pre-commit hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Expected output:
- markdown/yaml checks pass
- terraform checks pass or report "No Terraform files tracked yet"

## 4) Validate CI-equivalent checks locally

```bash
test -f README.md
test -f CONTRIBUTING.md
test -f SECURITY.md
test -d docs
```

Expected output:
- command exits with status `0`

## 5) Local visual dashboard validation

Use Docker Compose stack plus sample metric injection:

```bash
chmod +x scripts/local_dashboard_stack.sh scripts/inject_sample_metrics.sh
./scripts/local_dashboard_stack.sh up
./scripts/local_dashboard_stack.sh inject
```

Then open:

- Grafana: `http://localhost:3000` (`admin` / `admin`)
- Prometheus: `http://localhost:9090`

Reference: `docs/local-dashboard-validation.md`

## 6) Work with issues and milestones

1. Pick an issue from current milestone.
2. Create branch: `feat/<issue-id>-<slug>` or `chore/<issue-id>-<slug>`.
3. Open PR with linked issue and test evidence.

## 7) Verify board workflow

- Issue moves: `Todo` -> `In Progress` -> `Done`
- Keep one active `In Progress` item at a time.
