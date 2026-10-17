# m2-canary

| Champ | Valeur |
|---|---|
| Leçon | L11 |
| Type | guidé |
| Environnement | kind |
| Durée | à mesurer en jouant le lab |

## Objectif

10 % du trafic vers la nouvelle version, puis décider.

## État initial

un service en version 1.

## Ce que la validation contrôle sur l'état réel

la part de trafic demandée va à la version 2 (mesurée sur un lot de requêtes) ; la promotion ou l'annulation laisse un état cohérent.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m2-canary --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
