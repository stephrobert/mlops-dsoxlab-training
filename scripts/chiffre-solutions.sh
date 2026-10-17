#!/usr/bin/env bash
# Chiffre (ansible-vault) les fichiers en clair de solution/<lab>/ : à lancer
# avant tout commit. Mot de passe : .vault-pass, jamais versionné.
set -euo pipefail
cd "$(dirname "$0")/.."
for f in solution/*/*; do
  head -1 "$f" | grep -q '^\$ANSIBLE_VAULT' || \
    ansible-vault encrypt --vault-password-file .vault-pass "$f" >/dev/null
done
