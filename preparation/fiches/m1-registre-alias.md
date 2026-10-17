# m1-registre-alias

| Champ | Valeur |
|---|---|
| Leçon | L5 |
| Type | guidé |
| Environnement | mêmes conteneurs |
| Durée | à mesurer en jouant le lab |

## Objectif

Désigner un modèle par alias, sans chemin.

## État initial

le socle démarré avec un run existant.

## Ce que la validation contrôle sur l'état réel

un modèle est enregistré en version 1 puis 2 ; l'alias `challenger` pointe la bonne version ; la lignée remonte au run ; le chargement `models:/nom@challenger` fonctionne.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-registre-alias --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
