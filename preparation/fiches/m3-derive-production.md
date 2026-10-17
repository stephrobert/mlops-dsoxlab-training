# m3-derive-production

| Champ | Valeur |
|---|---|
| Leçon | L16 |
| Type | guidé |
| Environnement | kind, Prometheus, job Evidently |
| Durée | à mesurer en jouant le lab |

## Objectif

Alerte sur dérive réelle.

## État initial

un service servi, un flux de production sans dérive, puis avec dérive injectée par le générateur.

## Ce que la validation contrôle sur l'état réel

une alerte de dérive passe à `firing` sur le flux dérivé et reste silencieuse sans dérive.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab m3-derive-production --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
