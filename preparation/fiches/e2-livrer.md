# e2-livrer

| Champ | Valeur |
|---|---|
| Leçon | épreuve m2 |
| Type | challenge |
| Environnement | kind, S3, `act` |
| Durée | à mesurer en jouant le lab |

## Objectif

Prouver le niveau 2 sans indice : 60 min.

## État initial

cluster, registre et dépôt fournis.

## Ce que la validation contrôle sur l'état réel

`InferenceService` `READY=True` ; prédiction de référence ; canary sur la part demandée ; pipeline qui échoue avec le modèle dégradé sans bouger `champion`.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab e2-livrer --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
