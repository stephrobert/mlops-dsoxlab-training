# e1-reproduire

| Champ | Valeur |
|---|---|
| Leçon | épreuve m1 |
| Type | challenge |
| Environnement | conteneurs (socle complet) |
| Durée | à mesurer en jouant le lab |

## Objectif

Prouver le niveau 1 sans indice : 45 min.

## État initial

un dépôt avec jeu, code et socle ; un jeu au schéma cassé fourni.

## Ce que la validation contrôle sur l'état réel

`dvc status` propre ; empreinte des données dans S3 ; `dvc repro` du correcteur redonne la métrique attendue ; un run MLflow porte commit et empreinte ; l'alias `challenger` est posé ; la suite de tests échoue sur le schéma cassé.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab e1-reproduire --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
