# Faits mesurés des labs M1 L4 a L6 (2026-10-17, en cours)

Poste : mlflow 3.17.1 (serveur et client), scikit-learn 1.9.1, Python 3.14 du venv uv.

## m1-mlflow-serveur : VALIDE (avant 0/4, apres 4/4, rejeu 0/4, 40 s, commit afa43d5)

- `mlflow.sklearn.log_model(RandomForestRegressor)` echoue en 3.17.1 : `The saved sklearn model references untrusted types ... ['sklearn.tree._tree.Tree']` (format skops par defaut). Parade : `skops_trusted_types=["sklearn.tree._tree.Tree"]`. L'echec laisse un run FAILED avec params et metriques : les tests ne comptent que les FINISHED.
- Le modele n'est PAS sous les artefacts du run mais sous `<exp>/models/<model_id>/artifacts/` (MLmodel, model.skops 18 Mo, conda.yaml, python_env.yaml, requirements.txt) ; le lien run -> modele est `run.outputs.model_outputs[].model_id`. `list_artifacts(run)` rend [].
- MLflow pose seul le tag `mlflow.source.git.commit` (et branch) ; les tags `git_commit` et `data_sha256` sont ecrits par le script.
- Socle : `bash scripts/socle-demarrer.sh mlflow` (postgres, garage, mlflow, attend /health), ~10 s.
- Tests : API REST en urllib, PostgreSQL via `docker compose exec postgres psql -U mlflow -d mlflow -Atc "select run_uuid from runs ..."`, bucket via boto3 dans le conteneur mlflow.

## m1-registre-alias : NON TERMINE (prototype seulement)

- `mlflow.register_model("models:/<model_id>", nom)` fonctionne ; la version porte `run_id` et `source=models:/m-...`.
- `set_registered_model_alias`, `get_model_version_by_alias` fonctionnent.
- Stages : `transition_model_version_stage` et `get_latest_versions` marchent encore en 3.17.1 mais emettent un FutureWarning (deprecies depuis 2.9.0, "will be removed in a future major release") : enseigner les alias seulement.
- PIEGE BLOQUANT NON RESOLU : `mlflow.sklearn.load_model("models:/latence-service@champion")` se bloque (plus de 90 s) dans `_multipart_download` (http_artifact_repo) pour le fichier de 18 Mo, alors que `curl` du meme fichier via `/api/2.0/mlflow-artifacts/artifacts/...` rend 200 en 0,06 s, avec ou sans en-tete Range. A creuser : `MLFLOW_ENABLE_MULTIPART_DOWNLOAD=false`, ou taille de fichier (modele plus petit, n_arbres/max_depth), avant d'ecrire le lab.
- Un script tue en cours laisse des versions creees (1,2 puis 3,4) : le test doit raisonner sur l'etat, pas sur des numeros fixes.

## m1-tests-modele : NON COMMENCE
