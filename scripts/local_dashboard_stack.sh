#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"

if [[ -z "${ACTION}" ]]; then
  echo "Usage: $0 <up|inject|down|status>" >&2
  exit 1
fi

case "${ACTION}" in
  up)
    docker compose up -d
    ;;
  inject)
    ./scripts/inject_sample_metrics.sh
    ;;
  down)
    docker compose down
    ;;
  status)
    docker compose ps
    ;;
  *)
    echo "Unknown action: ${ACTION}" >&2
    echo "Usage: $0 <up|inject|down|status>" >&2
    exit 1
    ;;
esac
