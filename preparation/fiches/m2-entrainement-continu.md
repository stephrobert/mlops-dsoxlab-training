# m2-entrainement-continu

| Champ | Valeur |
|---|---|
| Leçon | L13 |
| Type | guidé |
| Environnement | kind |
| Durée | à mesurer en jouant le lab |

## Objectif

Réentraîner sans intervention ni risque.

## État initial

un CronJob d'entraînement désactivé.

## Ce que la validation contrôle sur l'état réel

le job tourne, enregistre un candidat sans toucher `champion` ; une exécution échouée ne laisse aucun état partiel.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-entrainement-continu --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
