#!/usr/bin/env bash
# Arrête le socle et efface ses volumes : le bucket repart vide.
set -euo pipefail
cd "$(dirname "$0")/../shared/socle"
docker compose down -v --remove-orphans
