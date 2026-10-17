# Scénario

`train.py` entraîne un modèle de latence à partir de `data/metriques.csv` et
affiche deux nombres. Rien n'est conservé : une semaine plus tard, personne ne
sait quels paramètres, quelles données et quel code ont donné le modèle
déployé. La pile du catalogue (MLflow sur `http://127.0.0.1:5000`, adossé à
PostgreSQL, artefacts dans le bucket S3 `mlflow-artefacts`) est démarrée avec
`bash scripts/socle-demarrer.sh mlflow` avant `dsoxlab run`.

## Mission

Dans un dépôt Git à vous (le répertoire de travail), avec `mlflow==3.17.1`
installé dans l'environnement du projet (la version du serveur) :

1. générez `data/metriques.csv` (graine 42, 5000 lignes) et commitez votre
   code ;
2. entraînez deux fois, chaque fois depuis un commit : d'abord avec
   `n_arbres: 50`, puis avec `n_arbres: 100`. Chaque run, dans une expérience
   de votre choix autre que `Default`, journalise les paramètres de
   `params.yaml`, les métriques `rmse` et `r2`, le modèle, un tag `git_commit`
   et un tag `data_sha256` (SHA-256 de `data/metriques.csv`) ;
3. taguez `v1` le commit du premier entraînement ;
4. écrivez dans `run-v1.txt` l'identifiant du run qui a produit le modèle de
   `v1`, puis commitez. L'arbre de travail doit être propre.
