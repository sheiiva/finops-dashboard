#!/usr/bin/env bash
set -euo pipefail

METRICS_FILE="${1:-config/examples/finops-sample-metrics.prom}"
PUSHGATEWAY_URL="${PUSHGATEWAY_URL:-http://localhost:9091}"
JOB_NAME="${JOB_NAME:-finops}"
INSTANCE_NAME="${INSTANCE_NAME:-local}"

if [[ ! -f "${METRICS_FILE}" ]]; then
  echo "ERROR: metrics file not found: ${METRICS_FILE}" >&2
  exit 1
fi

curl --fail --silent --show-error \
  --data-binary @"${METRICS_FILE}" \
  "${PUSHGATEWAY_URL}/metrics/job/${JOB_NAME}/instance/${INSTANCE_NAME}"

echo "OK: injected metrics from ${METRICS_FILE}"
