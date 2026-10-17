# m3-observer-inference

| Champ | Valeur |
|---|---|
| Leçon | L14 |
| Type | guidé |
| Environnement | kind et Prometheus |
| Durée | à mesurer en jouant le lab |

## Objectif

Voir le service avant le modèle.

## État initial

un service servi, sans métriques scrutées.

## Ce que la validation contrôle sur l'état réel

Prometheus scrute le service ; latence, trafic et erreurs sont interrogeables ; une requête PromQL donnée rend la valeur attendue.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m3-observer-inference --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
