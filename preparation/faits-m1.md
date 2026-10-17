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

## Rejeu des gestes ajoutés aux leçons (2026-10-17, dvc 3.67.1, projet jetable du scratchpad)

1. `dvc.lock` : `schema: '2.0'`, `hash: md5`, `md5`, `size`, `params: params.yaml: donnees.graine: 42` conformes à l'extrait de L3. Écarts : DVC replie `cmd` sur deux lignes (`--sortie` / `data/metriques.csv` à la ligne), trie `deps` par chemin (data/metriques.csv avant train.py) et les clés de `params` par ordre alphabétique ; `metrics.json` figure dans `outs` avec son md5 malgré `cache: false`.
2. Clone vierge : `uv sync --locked`, `dvc pull` (« 1 file fetched and 1 file added »), `dvc repro --force` rejoue `donnees` puis `entrainer` (rmse 23.31, r2 0.7813), `git diff metrics.json` : 0 ligne, `git status` propre.
3. `dvc cache dir` = `<projet>/.dvc/cache` (défaut). `git checkout <v1>` + `dvc checkout` : « M data/metriques.csv », SHA 550be1a3 ; `git switch -` : « Switched to branch 'main' » ; `dvc checkout` : SHA 65e665e5, branche main.
4. Sortie en double : `ERROR: output 'data/metriques.csv' is specified in:` / `- donnees` / `- data/metriques.csv.dvc` / `Use dvc remove with any of the above targets to stop tracking the overlapping output.` (rc 255). `dvc remove data/metriques.csv.dvc` (rc 0) : le CSV reste, `data/.gitignore` disparaît, le pointeur est supprimé (à commiter) ; `dvc repro` passe ensuite.
5. `dvc add` quand le `.gitignore` racine ignore déjà le CSV : succès sans message d'erreur, mais `data/.gitignore` n'est PAS écrit ; ensuite `git add data/.gitignore` donne `fatal: pathspec 'data/.gitignore' did not match any files`. Idem pour `metrics.json` ignoré à la racine (`git add` refuse). Parade : retirer ces deux lignes du `.gitignore` racine avant `dvc add` / avant le commit du pipeline. Rejoué avec cette parade : les `git add` des pages passent. La suppression du pointeur doit être ajoutée au commit (`git add data/metriques.csv.dvc` enregistre la suppression).

## Enchaînements de L3 rejoués de bout en bout (2026-10-17, dvc 3.67.1, uv 0.12.10)

- Cas (a), dépôt neuf : `git init`, `uv add dvc dvc-s3`, `dvc init`, remote, `dvc repro`. Sans `mkdir -p data`, l'étape `donnees` échoue : `FileNotFoundError: [Errno 2] No such file or directory: 'data/metriques.csv'` puis `ERROR: failed to reproduce 'donnees'` (DVC ne crée pas le dossier parent d'une sortie, le générateur non plus) ; le `git add` suivant donne alors `fatal: pathspec 'dvc.lock' did not match`. Avec `mkdir`, le `git add dvc.yaml dvc.lock params.yaml metrics.json train.py genere-metriques.py pyproject.toml uv.lock .dvc data/.gitignore .gitignore` passe, le dépôt est propre, `dvc push` : « 1 file pushed ». Le bucket ne contient qu'1 objet (metrics.json est en cache: false).
- Cas (b), suite de L2 : `dvc remove data/metriques.csv.dvc` (aucune sortie), `dvc repro`, `sed` sur metrics.json, `git add ... data/metriques.csv.dvc ...` passe et enregistre la suppression.
- Clone vierge des deux cas : `uv sync --locked`, `dvc pull` (« 1 file fetched and 1 file added »), `dvc repro --force`, rmse 23.31 / r2 0.7813, `git diff metrics.json` : 0 ligne.
- Dépannage « sorties absentes » : sur un clone SANS `dvc pull` (cache vide, bucket garni), `dvc status` dit `not in cache: data/metriques.csv`, et `dvc repro` NE PLANTE PAS : `Running stage 'donnees'` régénère le CSV (déterministe), `Stage 'entrainer' didn't change, skipping`, rc 0. Avec le CSV supprimé mais le cache présent : `Stage 'donnees' is cached - skipping run, checking out outputs`.
- `dvc params diff` après n_arbres 50 vers 60 : `params.yaml  entrainement.n_arbres  50  60`. `dvc metrics diff` : `r2 0.78135 -> 0.78608 (0.00473)`, `rmse 23.31062 -> 23.05688 (-0.25374)`.
