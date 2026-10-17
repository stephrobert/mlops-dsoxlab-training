# Faits mesurés des labs M1 L4 a L6 (2026-10-17, en cours)

Poste : mlflow 3.17.1 (serveur et client), scikit-learn 1.9.1, Python 3.14 du venv uv.

## m1-mlflow-serveur : VALIDE (avant 0/4, apres 4/4, rejeu 0/4, 40 s, commit afa43d5)

- `mlflow.sklearn.log_model(RandomForestRegressor)` echoue en 3.17.1 : `The saved sklearn model references untrusted types ... ['sklearn.tree._tree.Tree']` (format skops par defaut). Parade : `skops_trusted_types=["sklearn.tree._tree.Tree"]`. L'echec laisse un run FAILED avec params et metriques : les tests ne comptent que les FINISHED.
- Le modele n'est PAS sous les artefacts du run mais sous `<exp>/models/<model_id>/artifacts/` (MLmodel, model.skops 18 Mo, conda.yaml, python_env.yaml, requirements.txt) ; le lien run -> modele est `run.outputs.model_outputs[].model_id`. `list_artifacts(run)` rend [].
- MLflow pose seul le tag `mlflow.source.git.commit` (et branch) ; les tags `git_commit` et `data_sha256` sont ecrits par le script.
- Socle : `bash scripts/socle-demarrer.sh mlflow` (postgres, garage, mlflow, attend /health), ~10 s.
- Tests : API REST en urllib, PostgreSQL via `docker compose exec postgres psql -U mlflow -d mlflow -Atc "select run_uuid from runs ..."`, bucket via boto3 dans le conteneur mlflow.

## m1-registre-alias : VALIDE (avant 0/4, apres 4/4, rejeu 0/4, 40 s)

- `mlflow.register_model("models:/<model_id>", nom)` : la version porte `run_id` et `source=models:/m-...` ; `set_registered_model_alias` et `get_model_version_by_alias` fonctionnent. Un script interrompu laisse des versions creees (1,2 puis 3,4) : les tests raisonnent sur l'etat, jamais sur un numero fixe.
- Stages en 3.17.1 : `transition_model_version_stage` et `get_latest_versions` marchent encore mais emettent un FutureWarning ("deprecated since 2.9.0. Model registry stages will be removed in a future major release"). Le lab n'enseigne que les alias ; un test exige que toutes les versions restent en stage `None`.
- PIEGE (cause et parade, a citer dans la lecon) : `mlflow.sklearn.load_model("models:/nom@champion")` reste suspendu (plus de 90 s) sur `model.skops` (18 Mo). Cause : le serveur annonce par `/server-info` qu'il sait servir le telechargement multipart ; le client demande alors une URL presignee et telecharge par morceaux directement chez S3, a l'adresse interne `http://garage:3900`, injoignable depuis l'hote. `curl` du meme fichier par `/api/2.0/mlflow-artifacts/artifacts/...` rend 200 en 0,06 s. Parade cote client : `MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD=false` (chargement en 0,9 s). `MLFLOW_ENABLE_MULTIPART_DOWNLOAD=false` N'AGIT PAS sur ce chemin (essaye, toujours suspendu). Le serveur 3.17.1 n'offre pas d'interrupteur cote serveur reperage dans handlers.py. Le seuil de taille (`MLFLOW_MULTIPART_DOWNLOAD_MINIMUM_FILE_SIZE`) n'est pas la cause ici.
- Charge par alias : `mlflow.sklearn.load_model("models:/latence-service@challenger")` puis `predict(np.array([[60,70,150,0.02]]))`.

## m1-tests-modele : NON COMMENCE
