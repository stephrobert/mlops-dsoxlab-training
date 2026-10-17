# Faits mesurés du socle (2026-10-17)

Poste : Docker 29.1.3, Python 3.12.13, dsoxlab 0.5.3, uv 0.12.10. Clients dans un venv jetable : dvc 3.67.1, dvc-s3 3.3.0, mlflow 3.17.1, boto3 1.43.114.

## Images épinglées (digests relevés avec crane le 2026-10-17)

| Rôle | Image |
|---|---|
| S3 | dxflrs/garage:v2.4.1@sha256:9c96caa2612d3411acc5b0e6701fb238dbfba33e533a6d7d3d811a4b12d0d020 |
| MLflow | ghcr.io/mlflow/mlflow:v3.17.1-full@sha256:190306b1739b9646d6d39333594334b69ba14ab843db927712c790b50892f262 |
| PostgreSQL | postgres:17.11-alpine@sha256:b0f9560a2de083e2cc7382e75f808c7381a32852a7ec49117deedb300e552b24 |

Candidat non essayé : chrislusf/seaweedfs:4.48@sha256:4e61d15fd35994cb1e43e1e553dff106794841fd9a99ade2fc8c8bfce4d7872d.

## Choix du S3 : Garage

Garage a passé les deux essais réels. SeaweedFS n'a PAS été essayé (Garage suffisait au critère « les deux premiers essais passent ») : la comparaison n'est donc pas faite, elle reste à faire si l'on veut un second choix.

- MLflow : l'image `-full` est nécessaire (l'image sans suffixe n'embarque pas psycopg2 ni boto3 ; la `-full` contient psycopg2 2.9.13 et boto3 1.43.112). Serveur lancé avec `--artifacts-destination s3://mlflow-artefacts/ --serve-artifacts` ; le run `b2f62a32...` a son artefact vu dans le bucket : `1/<run>/artifacts/artefact-essai.txt`. `artifact_uri` côté client : `mlflow-artifacts:/1/<run>/artifacts` (le client passe par le serveur).
- DVC : `dvc remote add -d stockage s3://dvc-donnees`, `endpointurl http://127.0.0.1:3900`, `region garage`. `dvc push` : 1 file pushed ; `dvc pull` sur un clone Git vierge : 1 file fetched ; SHA-256 identique avant et après (550be1a3...) ; `dvc status` : « Data and pipelines are up to date ».
- Initialiseur de stockage KServe : NON ESSAYÉ (KServe ne se joue pas à cette étape) et documentation non consultée. À vérifier : KServe lit un S3 par `storage-initializer` avec un endpoint personnalisé (secret annoté `serving.kserve.io/s3-endpoint`).

## Pièges rencontrés

- Garage n'a pas de shell : toute commande passe par `docker compose exec garage /garage ...`. Après démarrage il faut assigner et appliquer une disposition (`layout assign`, `layout apply --version 1`), importer la clé (`key import`, identifiant `GK` + 24 hex, secret 64 hex) et donner les droits sur chaque bucket : tout est dans `shared/socle/init-garage.sh`, idempotent.
- Les secrets viennent d'un `.env` généré (`genere-env.sh`), ignoré par Git ; les noms `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` sont ceux que MLflow, boto3 et DVC lisent tels quels.
- PostgreSQL en `trust` sur le réseau interne Compose, sans port publié : le garde-fou du poste refuse un mot de passe dans une URL.
- `dvc-s3` n'installe pas boto3 : un script qui compte les objets du bucket doit l'ajouter.
- Ports : MLflow 5000, S3 3900, admin Garage 3903, tous sur 127.0.0.1. Nettoyage : `docker compose down -v` depuis `shared/socle/`, vérifié, aucun conteneur `mlops-socle` restant.

## Jeu de données fil rouge

`shared/genere-metriques.py`, bibliothèque standard, 5000 lignes par défaut. Graine 42, sans dérive : SHA-256 `550be1a31a70a78891b8bd57b5d02738593eff19198b858d532cf880d6b94880` sur deux exécutions (sortie standard, puis fichier `550be1a31a70a78891b8bd57b5d02738593eff19198b858d532cf880d6b94880`). Avec `--derive 0.5` (début à 50 %) : `23d3e7e267563608e90174ddf2dd15c816680a7ed87683851c9a0f44fd240bf6`. Mesure : sur la seconde moitié, latence moyenne 71,0 ms sans dérive, 121,0 ms avec, requêtes 129,0 contre 193,5 par seconde, incidents 9 contre 50. Le cycle de charge fait 120 minutes pour ne pas confondre saison et dérive (un cycle de 1440 minutes l'avait fait).
