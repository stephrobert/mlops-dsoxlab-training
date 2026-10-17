# Scenario

`train.py` trains a latency model from `data/metriques.csv` and prints two
numbers. Nothing is kept: a week later nobody can say which parameters, which
data and which code gave the model that is deployed. The catalogue's stack
(MLflow on `http://127.0.0.1:5000`, backed by PostgreSQL, artifacts in the S3
bucket `mlflow-artefacts`) is up. Start it with
`bash scripts/socle-demarrer.sh mlflow` before `dsoxlab run`.

## Mission

In a Git repository of your own (the work directory), with `mlflow==3.17.1`
installed in the project environment (the server version):

1. generate `data/metriques.csv` (seed 42, 5000 lines) and commit your code;
2. train twice, each time from a commit: first with `n_arbres: 50`, then with
   `n_arbres: 100`. Each run, in an experiment of your choice other than
   `Default`, logs the parameters of `params.yaml`, the metrics `rmse` and
   `r2`, the model, a tag `git_commit` and a tag `data_sha256` (SHA-256 of
   `data/metriques.csv`);
3. tag the commit of the first training `v1`;
4. write in `run-v1.txt` the id of the run that produced the model of `v1`,
   then commit. The working tree must be clean.
