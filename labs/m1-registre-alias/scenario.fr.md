# Scénario

`train.py` journalise déjà chaque entraînement sur le serveur MLflow
(`http://127.0.0.1:5000`, démarré par `bash scripts/socle-demarrer.sh mlflow`
avant `dsoxlab run`). Les modèles qu'il produit portent des ids opaques comme
`m-3f2a...` : personne ne sait lequel est en production. Le registre donne à un
modèle un nom, des versions numérotées et des alias.

## Mission

Dans le répertoire de travail (`mlflow==3.17.1` est déjà une dépendance ;
lancez `uv sync`, créez `data/` et générez `data/metriques.csv` avec la graine
42 et 5000 lignes d'abord) :

1. faites un dépôt Git, commitez, puis entraînez deux fois : `n_arbres: 50`,
   puis `n_arbres: 100` dans `params.yaml` (commit avant chaque run) ;
2. enregistrez les deux modèles sous le nom `latence-service` : la version 1
   vient du run à 50 arbres, la version 2 du run à 100 arbres ;
3. pointez l'alias `champion` sur la version à 50 arbres et `challenger` sur
   celle à 100 arbres. N'utilisez pas les stages du registre (dépréciés depuis
   MLflow 2.9) ;
4. écrivez `predire.py`, qui charge `models:/latence-service@challenger` (ni
   chemin, ni id de run, ni id `m-` dans le code) et affiche une prédiction de
   latence pour la ligne `cpu_pct=60, memoire_pct=70, requetes_s=150,
   taux_erreur=0.02`.

Attention : avec cette pile, le chargement d'un modèle peut rester suspendu.
Regardez `MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD`.
