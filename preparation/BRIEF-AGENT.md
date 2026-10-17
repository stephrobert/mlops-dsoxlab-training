# Brief : construire les labs de `mlops-dsoxlab-training`

Écrit le 2026-10-17. Cadrage : `todo/formation-mlops-cadrage.md` du site (§6 à §10). Décisions M1 à M12 validées le 2026-10-17.

## Mission

Créer les 19 labs de la fiche `fiches/`, un par un, dans l'ordre des leçons. **Règle B : lab avant guide.** Un lab ne se déclare dans `meta.yml` que le jour où il est écrit et joué.

## Règles

- `dsoxlab new lab <id> --runtime vm|shell` : jamais un `lab.yaml` écrit à la main, jamais une copie d'un lab voisin.
- Chaque lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail, 100 après la solution ; `dsoxlab clean` ne laisse rien.
- Notation sur l'état réel du système, jamais sur les commandes tapées.
- Images épinglées par `image:tag@sha256:...`. Aucun `:latest`.
- Aucun service tiers hors images de conteneurs et paquets déclarés. Aucune mention d'un assistant de rédaction dans le catalogue : ni fichier de consignes d'agent, ni ligne de co-auteur.
- Pas de push : la livraison est un geste de Stéphane.

## Socle fourni

- `shared/genere-metriques.py` : jeu fil rouge seedé, dérive par `--derive`.
- `shared/socle/` : PostgreSQL, Garage (S3), MLflow. `bash genere-env.sh`, `docker compose up -d postgres garage`, `bash init-garage.sh`, `docker compose up -d mlflow`.
- Faits mesurés et pièges : `preparation/faits-socle.md`.

## Non joué à ce jour

KServe (mode Standard, kind), Prometheus, Evidently, `act`, SeaweedFS et l'initialiseur de stockage KServe sur Garage.
