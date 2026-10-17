#!/usr/bin/env bash
# Demarre le socle. Sans argument : le stockage S3 (Garage) seul. Avec
# `mlflow` : PostgreSQL, Garage et le serveur MLflow (a jouer avant `dsoxlab run`).
set -euo pipefail
cd "$(dirname "$0")/../shared/socle"
bash genere-env.sh
if [ "${1:-}" = "mlflow" ]; then
  docker compose up -d postgres garage
  bash init-garage.sh
  docker compose up -d mlflow
  for _ in $(seq 1 60); do
    curl -fsS http://127.0.0.1:5000/health >/dev/null 2>&1 && { echo "mlflow pret"; exit 0; }
    sleep 1
  done
  echo "mlflow ne repond pas sur /health" >&2
  exit 1
fi
docker compose up -d garage
bash init-garage.sh
