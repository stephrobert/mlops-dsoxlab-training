# Scénario

Une collègue vous passe `train.py` : un modèle qui prédit la latence p95 d'un
service à partir de sa charge. Elle a annoncé un RMSE de 23 ms. Vous le lancez
deux fois : vous obtenez deux valeurs différentes, et aucune n'est la sienne.
Elle ne sait plus quelles versions de bibliothèques elle avait installées, ni
avec quel jeu de données elle a travaillé. Le générateur de métriques
`genere-metriques.py` produit le jeu fil rouge du catalogue.

Personne ne peut aujourd'hui dire si un écart de métrique vient du code, des
données, des bibliothèques ou du hasard.

## Mission

Livrez un projet dont deux entraînements donnent exactement les mêmes
métriques, sur n'importe quel poste qui le clone. Le jeu attendu : graine 42,
5000 lignes, dans `data/metriques.csv`. Le projet est un dépôt Git propre,
son environnement vit dans `.venv`, et la graine se règle dans `params.yaml`
(clé `seed`). Il vous revient de trouver d'où vient la variation, et ce qu'il
faut versionner pour qu'un autre obtienne le même résultat.
