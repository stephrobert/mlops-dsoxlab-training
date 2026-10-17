# m3-rollback

| Champ | Valeur |
|---|---|
| Leçon | L17 |
| Type | guidé |
| Environnement | kind |
| Durée | à mesurer en jouant le lab |

## Objectif

Revenir à un modèle sain, joué hors incident.

## État initial

un `champion` dégradé en service.

## Ce que la validation contrôle sur l'état réel

l'alias `champion` est repointé ; l'`InferenceService` sert de nouveau le modèle sain ; la prédiction de référence est retrouvée.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m3-rollback --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
