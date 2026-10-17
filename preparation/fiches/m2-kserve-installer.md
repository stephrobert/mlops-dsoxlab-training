# m2-kserve-installer

| Champ | Valeur |
|---|---|
| Leçon | L9 |
| Type | guidé |
| Environnement | kind |
| Durée | à mesurer en jouant le lab |

## Objectif

Plan de contrôle KServe prêt (mode Standard).

## État initial

un cluster kind vierge.

## Ce que la validation contrôle sur l'état réel

les déploiements KServe sont `Available` ; le CRD `InferenceService` existe ; versions épinglées.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-kserve-installer --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
