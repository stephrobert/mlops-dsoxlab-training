# Rendre un modèle reproductible et traçable

## Situation

Le modèle de latence du fil rouge est entraîné à la main : personne ne sait le
reconstruire ni dire quel code et quelles données l'ont produit. La pile du
catalogue est démarrée (`bash scripts/socle-demarrer.sh mlflow`) : stockage S3
(bucket `dvc-donnees`, `http://127.0.0.1:3900`, région `garage`, clés dans
`shared/socle/.env`) et serveur MLflow (`http://127.0.0.1:5000`,
`mlflow==3.17.1`). Le dépôt de départ est le bundle `depot.bundle` :
clonez-le avec `git clone depot.bundle projet` et travaillez dans `projet/`.
Le fichier `casse-schema.csv`, à côté du bundle, est un jeu dont le schéma est
cassé.

## Ce qui est attendu

Dans `projet/`, commité dans Git (l'arbre de travail doit être propre), graine
42 et paramètres de `params.yaml` inchangés :

1. les données sont versionnées par DVC et poussées dans le stockage S3 ;
   `dvc status` est propre et le stockage est synchronisé ;
2. la génération des données et l'entraînement forment un pipeline DVC dont
   vous nommez les étapes `donnees` et `entrainer` ; sur un clone vierge, une
   fois l'environnement reconstruit depuis le verrou et les données tirées,
   `dvc repro` redonne les métriques du dépôt (RMSE 23,31 ms) ;
3. l'entraînement journalise sur le serveur MLflow, dans un run terminé, ses
   paramètres, ses métriques et son modèle, avec les tags `git_commit` (un
   commit du dépôt) et `data_sha256` (SHA-256 de `data/metriques.csv`) ;
4. le modèle de ce run est enregistré sous le nom `latence-service`, et
   l'alias `challenger` pointe la version construite par ce run ;
5. une suite pytest dans `tests/` lit le jeu dans la variable d'environnement
   `DONNEES` (défaut `data/metriques.csv`) et les métriques dans `METRIQUES`
   (défaut `metrics.json`), et échoue sur `casse-schema.csv` (colonnes
   manquantes) comme sur un fichier de métriques dont le `rmse` dépasse
   `rmse_max`, un seuil lu dans le fichier versionné `seuils.yaml`, qui laisse passer votre
   modèle et au plus `28.0`. Elle passe sur les données et les métriques du dépôt.

## Ce qui est noté

L'état de `projet/`, du stockage S3 et du serveur MLflow, jamais les commandes
tapées : le correcteur clone votre dépôt, rejoue le pipeline et lance votre
suite sur ses propres jeux et fichiers de métriques. Aucun indice n'est
proposé : l'épreuve mesure ce que vous savez déjà faire. Seuil de réussite :
70 points.
