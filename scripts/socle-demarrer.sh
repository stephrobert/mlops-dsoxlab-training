#!/usr/bin/env bash
# Démarre le stockage S3 (Garage) du socle. À jouer avant `dsoxlab run`.
set -euo pipefail
cd "$(dirname "$0")/../shared/socle"
bash genere-env.sh
docker compose up -d garage
bash init-garage.sh
