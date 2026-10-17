# m2-kserve-servir

| Champ | Valeur |
|---|---|
| Leçon | L10 |
| Type | guidé |
| Environnement | kind et S3 |
| Durée | à mesurer en jouant le lab |

## Objectif

Servir le modèle du registre avec un `InferenceService`.

## État initial

KServe installé, un modèle dans le bucket S3.

## Ce que la validation contrôle sur l'état réel

`InferenceService` `READY=True` ; la prédiction de référence passe par l'API ; l'initialiseur de stockage a lu le S3.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-kserve-servir --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
