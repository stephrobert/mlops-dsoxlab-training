# m1-tests-modele

| Champ | Valeur |
|---|---|
| Leçon | L6 |
| Type | guidé |
| Environnement | poste |
| Durée | à mesurer en jouant le lab |

## Objectif

Refuser un modèle moins bon, et des données au schéma cassé.

## État initial

un modèle de référence, un jeu valide et un jeu au schéma cassé fourni.

## Ce que la validation contrôle sur l'état réel

la suite pytest échoue sur le jeu cassé et sur le modèle dégradé, passe sur les valides ; le seuil est lu dans un fichier versionné.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-tests-modele --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
