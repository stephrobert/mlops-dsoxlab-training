# Faits de l'épreuve e1-reproduire (2026-10-17)

Poste : dsoxlab 0.5.3, uv 0.12.10, DVC 3.67.1, mlflow 3.17.1, scikit-learn 1.9.1, Garage v2.4.1.

## Spécification retenue

- `lab_type: challenge`, `exam_passing_score: 70`, 45 min annoncées, `level: m1`, section `level-exams` de `meta.yml` (forme du catalogue frère dev-pour-ops, qui utilise `capstone` pour ses épreuves ; `challenge` suit la consigne). Aucun indice. `doc_url` PROVISOIRE : `/docs/mlops/tests-modele/`, à décider avec le site.
- Point de départ : `depot.bundle` (un commit : `genere-metriques.py`, `train.py` du pipeline L3, `params.yaml`, `pyproject.toml` avec dvc[s3], mlflow==3.17.1, pandas, pytest, `uv.lock`) à cloner dans `projet/`, et `casse-schema.csv` (60 lignes, `memoire_pct` renommée `mem_pct`). Ni DVC, ni suivi, ni tests, ni `data/` : tout est à faire.
- Livrables : données suivies par DVC et poussées ; pipeline `donnees` + `entrainer` ; run MLflow FINISHED avec tags `git_commit` et `data_sha256` ; modèle `latence-service` avec alias `challenger` ; suite pytest lisant `DONNEES` et `METRIQUES` et un seuil `rmse_max` (au plus 28,0) dans `seuils.yaml`.
- Compétences : ml.data.version (dvc status, S3), ml.pipeline.reproduce (clone vierge), ml.experiment.track (run tracé), ml.model.register (alias), ml.model.validate (suite de tests : schéma et seuil de métrique). La validation du modèle se fait ici sur `metrics.json` (seuil versionné), variante simplifiée du calcul sur joblib de L6.

## Tests (7, un par exigence)

dépôt propre et `dvc status` / `dvc status -c` ; clé `files/md5/<2>/<30>` du CSV dans le bucket `dvc-donnees` (liste faite par boto3 dans le conteneur mlflow) ; clone vierge (`uv sync --frozen`, `dvc pull`, `dvc repro --force`, métriques identiques, RMSE 23,31 et R2 0,7813) ; run FINISHED à tags exacts ; alias `challenger` vers un run tracé ; suite qui passe sur le bon et échoue sur `casse-schema.csv` ; suite qui échoue sur un `metrics.json` à rmse 40 et lit `seuils.yaml`.

## Scores

Sans solution 0/7, avec solution 7/7 (100), rejeu après clean 0/7, 53 s. Essai négatif (solution privée de `dvc push`, de l'enregistrement et avec `rmse_max: 99.0`) : 2/7, les cinq tests concernés échouent (clone vierge, dépôt/dvc status, S3, alias, seuil).

## Pièges

- Le correcteur lance un `dvc repro --force` sur le clone : le train.py instrumenté y journalise un run de plus dans MLflow (commit du clone, mêmes données). Le serveur doit donc répondre pendant la notation.
- `mkdir -p data` (piège L3) reste à la charge de l'apprenant ; sans lui `dvc repro` échoue.
- Le chargement du modèle par alias n'est pas exigé (le piège du téléchargement multipart de L5 n'est pas rejoué ici).
