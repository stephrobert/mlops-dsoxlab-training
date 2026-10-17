#!/usr/bin/env bash
# Génère `.env` (ignoré par Git) avec des secrets aléatoires, une seule fois.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && exit 0
{
  printf 'AWS_ACCESS_KEY_ID=GK%s\n' "$(openssl rand -hex 12)"
  printf 'AWS_SECRET_ACCESS_KEY=%s\n' "$(openssl rand -hex 32)"
  printf 'GARAGE_RPC_SECRET=%s\n' "$(openssl rand -hex 32)"
  printf 'GARAGE_ADMIN_TOKEN=%s\n' "$(openssl rand -hex 16)"
} > .env
chmod 600 .env
