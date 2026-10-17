# m2-cicd-modele

| Champ | Valeur |
|---|---|
| Leçon | L12 |
| Type | guidé |
| Environnement | `act` et kind |
| Durée | à mesurer en jouant le lab |

## Objectif

Un pipeline qui refuse un modèle moins bon.

## État initial

un workflow GitHub Actions et un dépôt.

## Ce que la validation contrôle sur l'état réel

le workflow passe avec le bon modèle, échoue avec le modèle dégradé fourni, sans bouger l'alias `champion`.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-cicd-modele --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
