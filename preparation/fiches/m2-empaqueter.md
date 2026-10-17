# m2-empaqueter

| Champ | Valeur |
|---|---|
| Leçon | L7 |
| Type | guidé |
| Environnement | Docker |
| Durée | à mesurer en jouant le lab |

## Objectif

Un modèle qui répond hors notebook.

## État initial

un modèle du registre.

## Ce que la validation contrôle sur l'état réel

une image épinglée par digest sert une prédiction HTTP ; la prédiction de référence est exacte ; le conteneur tourne sans privilège.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-empaqueter --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
