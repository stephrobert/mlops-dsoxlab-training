#!/usr/bin/env bash
# Initialise Garage : disposition à un noeud, clé d'accès, deux buckets.
# Idempotent ; à lancer après `docker compose up`.
set -euo pipefail
cd "$(dirname "$0")"
source ./.env
G=(docker compose exec -T garage /garage)
for _ in $(seq 1 30); do "${G[@]}" status >/dev/null 2>&1 && break; sleep 1; done
ID=$("${G[@]}" node id 2>/dev/null | head -1 | cut -d@ -f1)
if ! "${G[@]}" layout show | grep -q "$ID"; then
  "${G[@]}" layout assign -z dc1 -c 1G "$ID"
  "${G[@]}" layout apply --version 1
fi
"${G[@]}" key info "$AWS_ACCESS_KEY_ID" >/dev/null 2>&1 || "${G[@]}" key import --yes -n lab "$AWS_ACCESS_KEY_ID" "$AWS_SECRET_ACCESS_KEY"
for b in mlflow-artefacts dvc-donnees; do
  "${G[@]}" bucket info "$b" >/dev/null 2>&1 || "${G[@]}" bucket create "$b"
  "${G[@]}" bucket allow --read --write --owner "$b" --key "$AWS_ACCESS_KEY_ID"
done
echo "garage pret"
