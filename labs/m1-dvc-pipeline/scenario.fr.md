# Scénario

Dans ce dépôt, on génère les données avec `genere-metriques.py` puis on lance
`train.py`, à la main, dans cet ordre. La graine et les hyperparamètres sont
dans `params.yaml`. Quand une collègue change `n_arbres`, personne ne sait s'il
faut aussi régénérer les données, et les métriques publiées n'ont jamais pu
être refaites par quelqu'un d'autre. Le socle S3 du catalogue (bucket
`dvc-donnees`, `http://127.0.0.1:3900`, région `garage`, clés dans
`shared/socle/.env`) est disponible.

## Mission

Livrez un dépôt dont le pipeline (données, puis entraînement) est décrit et
versionné, avec ses sorties dans le bucket. Un clone vierge, dont l'environnement
est reconstruit depuis le verrou, doit redonner les mêmes métriques. Un `dvc
repro` sans changement ne doit rien rejouer, et modifier `n_arbres` ne doit
rejouer que l'étape d'entraînement, que vous nommerez `entrainer`.
