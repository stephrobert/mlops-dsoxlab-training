# m1-dvc-pipeline

| Champ | Valeur |
|---|---|
| Leçon | L3 |
| Type | guidé |
| Environnement | conteneur S3 (Garage) |
| Durée | à mesurer en jouant le lab |

## Objectif

Rejouer l'entraînement à l'identique par `dvc repro`.

## État initial

le dépôt du lab précédent avec ses données suivies.

## Ce que la validation contrôle sur l'état réel

`dvc.yaml` décrit les étapes ; `dvc repro` rejoue sans rien recalculer quand rien ne change ; changer un paramètre ne relance que l'étape touchée ; les métriques attendues sortent.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-dvc-pipeline --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
