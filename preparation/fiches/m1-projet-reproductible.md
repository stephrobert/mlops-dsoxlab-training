# m1-projet-reproductible

| Champ | Valeur |
|---|---|
| Leçon | L1 |
| Type | guidé |
| Environnement | poste (Python) |
| Durée | à mesurer en jouant le lab |

## Objectif

Obtenir deux fois les mêmes métriques d'un entraînement.

## État initial

un dossier de projet vide, le générateur `shared/genere-metriques.py`.

## Ce que la validation contrôle sur l'état réel

le script d'entraînement, la graine et les dépendances sont versionnés ; deux exécutions donnent les mêmes métriques (empreinte identique).

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-projet-reproductible --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
