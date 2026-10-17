# m1-mlflow-serveur

| Champ | Valeur |
|---|---|
| Leçon | L4 |
| Type | guidé |
| Environnement | conteneurs MLflow, PostgreSQL, S3 |
| Durée | à mesurer en jouant le lab |

## Objectif

Savoir quel run a produit quel modèle.

## État initial

le socle `shared/socle/` arrêté ; un script d'entraînement sans suivi.

## Ce que la validation contrôle sur l'état réel

le serveur répond sur `/health` ; un run porte paramètres, métriques, commit Git et empreinte des données ; son artefact est dans le bucket S3 ; les métadonnées survivent à un redémarrage du serveur (PostgreSQL).

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m1-mlflow-serveur --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
