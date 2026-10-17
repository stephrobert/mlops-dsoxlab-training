# Faits mesurés des labs M1 (2026-10-17)

Poste : dsoxlab 0.5.3, uv 0.12.10, Docker 29.1.3, socle Garage de `faits-socle.md`.
Rejeu : `python3 scripts/valider-labs.py --lab <id>` (clean, socle, run, check, solution, check, cleanup).

| Lab | Sans solution | Avec solution | Durée du rejeu |
|---|---|---|---|
| m1-projet-reproductible | 0 | 100 (6 tests) | 9-10 s |
| m1-dvc-donnees | 0 | 100 (5 tests) | 20 s |
| m1-dvc-pipeline | 0 | 100 (4 tests) | 25 s |

## Résultats utiles à l'author

- `uv add numpy scikit-learn pyyaml` installe scikit-learn 1.9.1, scipy 1.18.1, threadpoolctl 3.7.0 (8 paquets). Avec `random_state` sur le découpage ET sur `RandomForestRegressor` (n_jobs=1), RMSE 23,31 ms et R2 0,781 (graine 42, 5000 lignes, 4 entrées, cible latence_p95_ms).
- Deux sources d'aléa dans le script de l'apprenant : le découpage train/test et la forêt. N'en corriger qu'une laisse les métriques instables : c'est le diagnostic du lab L1.
- Jeu de graine 42 : SHA-256 550be1a3... ; graine 43 : 65e665e5...
- `dvc status -c` répond « Cache and remote 'stockage' are in sync. » et NON « up to date » (qui est la réponse de `dvc status` local, « Data and pipelines are up to date. »).
- Bucket Garage : `docker compose exec -T garage /garage bucket info dvc-donnees` donne une ligne `Objects:`.
- `dvc repro` sans changement : aucune ligne « Running stage », « Stage ... didn't change, skipping ». Un `n_arbres` modifié rejoue `entrainer` seul ; `donnees` n'est pas relancée.
- Un `metrics:` en `cache: false` reste dans Git (`metrics.json` versionné), pas dans le bucket.

## Pièges

- `dsoxlab run` ouvre un shell interactif : l'automatiser avec `</dev/null`. `dsoxlab clean` demande « y/N » sur l'entrée standard.
- `setup.sh` et `cleanup.sh` sont INTERDITS dans un lab `shell` par `validate-structure` (ils sont réservés aux labs `vm`, en `setup.yaml`/`cleanup.yaml` Ansible). Le démarrage du socle est donc dans `scripts/socle-demarrer.sh` et `scripts/socle-arreter.sh` ; l'apprenant les lance avant `dsoxlab run`.
- `validate-structure` refuse une solution en clair : elle est chiffrée par `ansible-vault` (`scripts/chiffre-solutions.sh`, mot de passe `.vault-pass`, ignoré par Git). Sans `.vault-pass`, le rejeu est impossible.
- Une fixture en lien symbolique (`genere-metriques.py` vers `shared/`) est copiée comme fichier dans le workdir.
- Le catalogue n'a pas de `lab.en.yaml` : `lab.yaml` est l'anglais canonique, `lab.fr.yaml` la surcharge, comme les frères.
- Le `lab.yaml` généré n'a pas de `solution`/`hints` : aucun indice écrit à ce stade.
- Le hook du poste refuse `rm -r` d'un workdir : passer par `dsoxlab clean`.
- Python des tests : celui de dsoxlab (3.14, pytest embarqué), pas celui de mise.

## Non joué

- Les indices (`hints.yaml`) des trois labs.
- Un apprenant réel : aucun essai humain, le temps réel (30 à 40 min annoncées) n'est pas mesuré.
- Le rejeu sur un poste sans cache uv (premier `uv add` : réseau PyPI, durée non mesurée à froid).
- Ordre L2 puis L3 enchaînés sur le même bucket : chaque rejeu repart d'un bucket vide (`down -v`).
