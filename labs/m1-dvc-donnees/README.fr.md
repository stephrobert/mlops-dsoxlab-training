# m1-dvc-donnees

**Public :** l'apprenant.

Versionner un jeu de données avec DVC et un remote S3, et le retrouver à
l'identique.

## Prérequis

Docker, `uv`, `git`, avoir joué `m1-projet-reproductible`. Démarrer le socle
avant `dsoxlab run` : `bash scripts/socle-demarrer.sh`. Les clés S3 sont dans
`shared/socle/.env` (à exporter : `set -a; source shared/socle/.env; set +a`).
Arrêt : `bash scripts/socle-arreter.sh`.
