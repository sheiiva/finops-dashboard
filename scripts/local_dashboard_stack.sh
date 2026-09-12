#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"

if [[ -z "${ACTION}" ]]; then
  echo "Usage: $0 <up|inject|inject-csv|inject-gcp|down|status>" >&2
  exit 1
fi

case "${ACTION}" in
  up)
    docker compose up -d
    ;;
  inject)
    # Legacy multi-cloud sample; prefer inject-csv for v1 slim pack.
    ./scripts/inject_sample_metrics.sh
    ;;
  inject-csv)
    python3 ./scripts/csv_billing_to_metrics.py
    ./scripts/inject_sample_metrics.sh config/examples/finops-csv-metrics.prom
    ;;
  inject-gcp)
    python3 ./scripts/gcp_build_finops_export_table.py
    args=(--push --pushgateway-url "${PUSHGATEWAY_URL:-http://localhost:9091}")
    if [[ -n "${GCP_PROJECT_ID:-}" ]]; then
      args+=(--project-id "${GCP_PROJECT_ID}")
    fi
    if [[ -n "${BILLING_EXPORT_TABLE:-}" ]]; then
      args+=(--billing-table "${BILLING_EXPORT_TABLE}")
    fi
    python3 ./scripts/gcp_finops_api_snapshot.py "${args[@]}"
    ;;
  down)
    docker compose down
    ;;
  status)
    docker compose ps
    ;;
  *)
    echo "Unknown action: ${ACTION}" >&2
    echo "Usage: $0 <up|inject|inject-csv|inject-gcp|down|status>" >&2
    exit 1
    ;;
esac
