# Scenario

`train.py` already logs each training on the MLflow server
(`http://127.0.0.1:5000`, started with `bash scripts/socle-demarrer.sh mlflow`
before `dsoxlab run`). The models it produces are identified by opaque ids
such as `m-3f2a...`: nobody can say which one is in production. The registry
gives a model a name, numbered versions and aliases.

## Mission

In the work directory (`mlflow==3.17.1` is already a dependency; run
`uv sync`, create `data/` and generate `data/metriques.csv` with seed 42 and
5000 lines first):

1. make a Git repository, commit, then train twice: `n_arbres: 50`, then
   `n_arbres: 100` in `params.yaml` (commit before each run);
2. register both models under the name `latence-service`: version 1 comes from
   the 50-tree run, version 2 from the 100-tree run;
3. point the alias `champion` at the 50-tree version and `challenger` at the
   100-tree version. Do not use registry stages (deprecated since MLflow 2.9);
4. write `predire.py`, which loads `models:/latence-service@challenger` (no
   path, no run id, no `m-` id in the code) and prints one latency prediction
   for the row `cpu_pct=60, memoire_pct=70, requetes_s=150, taux_erreur=0.02`.

Careful: with this stack, loading a model may hang. Look at
`MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD`.
