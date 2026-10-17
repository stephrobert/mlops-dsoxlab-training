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

## Complément ml.model.validate (2026-10-17, suite à la revue skills-guardian)

- Fixtures ajoutées : `casse-bornes.csv` (60 lignes, schéma intact, cpu 140, taux_erreur -0.5, requetes_s -12, latence 0) et `metrics-champion.json` (`rmse` 22.413..., `r2` 0.7979 : le champion à 100 arbres du lab L6).
- Forme choisie pour le champion : un fichier de métriques, pas un `champion.joblib`. L'épreuve note déjà `metrics.json` produit par le pipeline ; un joblib obligerait l'apprenant à sauvegarder un modèle hors de ce qu'enseigne le pipeline, et pèserait 19 Mo (100 arbres). La logique testée reste celle de L6 (RMSE du candidat <= RMSE du champion + tolérance), avec une variante annoncée : L6 écrit la tolérance en dur (`TOLERANCE_MS = 1.0` dans le test) alors que l'épreuve la déplace dans `seuils.yaml` (`tolerance_ms`), lue par la suite. Le modèle de l'apprenant (23,31) dépasse le champion (22,41) de 0,9 ms : il passe pour toute tolérance d'au moins 0,8972 ms (23,3106 - 22,4134) et le candidat de test à 25,5 (3,0866 ms au-dessus) est refusé pour toute tolérance strictement inférieure à 3,0866 ms : plage valide [0,8972 ; 3,0866[ ; 3,0 refuse bien 25,5.
- 9 tests (au lieu de 7). Les garde-fous sont isolés dans une copie temporaire du dépôt dont `seuils.yaml` est modifié : tolérance relevée à 100 pour le seuil absolu (candidat rmse 40), `rmse_max` relevé à 100 pour la comparaison au champion (candidat rmse 25,5, soit 3,1 ms au-dessus). Sans cela le candidat refusé l'aurait été par les deux garde-fous.
- Scores : 0/9, 9/9 (100), rejeu 0/9, 55 s. Essai négatif (suite qui ignore le champion, `assert True`) : 8/9, seul `test_la_suite_refuse_un_candidat_moins_bon_que_le_champion` échoue.

## Audit du challenger (2026-10-17) : 11 tests

- Tests ajoutés : forme du pipeline (`dvc.yaml` : étapes `donnees` et `entrainer`, `entrainer` dépend de `data/metriques.csv` et déclare des params `entrainement*`, `donnees` produit le CSV et déclare des params) ; aucune clé d'accès (`access_key`, `secret_access`, `session_token`) dans le `.dvc/config` du dernier commit, qui déclare `s3://dvc-donnees` (racine du bucket).
- Contrôles de texte « lit seuils.yaml » / « lit tolerance_ms » remplacés par du comportement, sur une copie : `rmse_max` abaissé à 20 puis `tolerance_ms` abaissé à 0,5 font chacun échouer la suite sur les bonnes métriques.
- S6 : l'état du serveur MLflow (runs, alias, versions) ET celui du bucket survivent à `dsoxlab clean` + `dsoxlab run` (seul le répertoire de travail est refait). Mesuré avant correction : après clean + run et un travail partiel (clone, `uv sync`, CSV généré), 3/9 tests passaient (run, alias, clé S3 périmés). Correction : un run ne compte que si son `start_time` est postérieur à la création de `depot.bundle` dans le répertoire de travail (ctime). Après correction, même essai : 1/11 (reste la clé de l'empreinte dans le bucket, périmée ; `dvc status -c` échoue, donc aucun point utile sans travail). Recommandation (README) : repartir d'un socle neuf pour une nouvelle tentative.
- Essais négatifs : clé d'accès ajoutée dans `.dvc/config` -> 8/11 (clé, clone, status échouent) ; `entrainer` sans params ni dépendance -> 10/11 (test de pipeline seul) ; seuil et tolérance en dur -> 9/11 (les deux tests de comportement).
