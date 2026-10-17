# Scenario

The latency model is promoted when its RMSE "looks fine", on a CSV nobody
inspects. Two incidents already happened: a column renamed upstream, and
impossible values (CPU at 140 %). This lab needs no server: everything runs in
the work directory.

## Mission

In the work directory (`uv sync`, then create `data/` and generate
`data/metriques.csv` with seed 42 and 5000 lines; make a Git repository):

1. train a champion and a candidate with `train.py` (for instance 100 trees
   into `modele/champion.joblib` and `modele/candidat.joblib`);
2. write `seuils.yaml`, committed, with the key `rmse_max` (at most `28.0`);
3. write a pytest suite in `tests/` that reads three environment variables,
   with these defaults: `DONNEES` (`data/metriques.csv`), `MODELE`
   (`modele/candidat.joblib`) and `CHAMPION` (`modele/champion.joblib`). It
   must check:
   - the schema: the columns `cpu_pct`, `memoire_pct`, `requetes_s`,
     `taux_erreur`, `latence_p95_ms` exist;
   - the bounds: `cpu_pct` and `memoire_pct` in [0, 100], `taux_erreur` in
     [0, 1], `requetes_s` at least 0, `latence_p95_ms` above 0;
   - the model: its RMSE on the test part (same split as `train.py`,
     `params.yaml`: `part_test` and `seed`) is at most `rmse_max`, and at most
     1.0 ms above the RMSE of the champion;
4. commit everything. The check replays your suite with its own datasets
   (`casse-schema.csv`, `casse-bornes.csv` and a valid one) and its own models
   (good, too weak, worse than the champion): it must pass on the valid ones
   and fail (tests failing, exit code 1) on the others.
