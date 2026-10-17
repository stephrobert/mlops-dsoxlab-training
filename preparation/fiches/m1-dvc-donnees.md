# m1-dvc-donnees

| Champ | Valeur |
|---|---|
| Leçon | L2 |
| Type | guidé |
| Environnement | conteneur S3 (Garage) |
| Durée | à mesurer en jouant le lab |

## Objectif

Retrouver une version exacte du jeu de données.

## État initial

un dépôt Git sans DVC, le socle S3 démarré.

## Ce que la validation contrôle sur l'état réel

`dvc status` propre ; l'empreinte du jeu est dans le bucket ; un `dvc pull` sur un clone vierge redonne le même SHA-256 ; une seconde version du jeu est retrouvable par `git checkout`.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-dvc-donnees --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
