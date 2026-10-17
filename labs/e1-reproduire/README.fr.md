# e1-reproduire

**Public :** l'apprenant.

Épreuve du niveau 1 : rendre un modèle reproductible et traçable, sans indice.

## Prérequis

Docker, `uv`, `git`, les leçons et labs du niveau 1. Démarrer la pile avant
`dsoxlab run` : `bash scripts/socle-demarrer.sh mlflow`. Arrêt :
`bash scripts/socle-arreter.sh`. Clés S3 :
`set -a; source shared/socle/.env; set +a`.

Pour une nouvelle tentative, arrêtez puis redémarrez la pile
(`bash scripts/socle-arreter.sh` puis `bash scripts/socle-demarrer.sh mlflow`) :
`dsoxlab clean` ne vide ni le bucket ni le serveur MLflow.
