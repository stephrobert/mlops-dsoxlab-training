# m3-carte-de-modele

| Champ | Valeur |
|---|---|
| Leçon | L18 |
| Type | guidé |
| Environnement | conteneurs MLflow |
| Durée | à mesurer en jouant le lab |

## Objectif

Prouver d'où vient un modèle.

## État initial

un modèle du registre.

## Ce que la validation contrôle sur l'état réel

la carte de modèle (données, code, métriques, limites) est rattachée à la version et complète ; la lignée remonte jusqu'au commit.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m3-carte-de-modele --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
