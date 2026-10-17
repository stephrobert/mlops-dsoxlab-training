# Make a model reproducible and traceable

## Situation

The latency model of the thread is trained by hand: nobody can rebuild it nor
say which code and which data produced it. The stack of the catalogue is up
(`bash scripts/socle-demarrer.sh mlflow`): S3 store (bucket `dvc-donnees`,
`http://127.0.0.1:3900`, region `garage`, keys in `shared/socle/.env`) and
MLflow server (`http://127.0.0.1:5000`, `mlflow==3.17.1`). The starting
repository is the bundle `depot.bundle`: clone it with
`git clone depot.bundle projet` and work in `projet/`. The file
`casse-schema.csv`, next to the bundle, is a dataset whose schema is broken.

## What is expected

In `projet/`, committed in Git (the working tree must be clean), seed 42 and
the parameters of `params.yaml` left unchanged:

1. the data is versioned by DVC and pushed to the S3 store; `dvc status` is
   clean and the store is in sync;
2. the data generation and the training are a DVC pipeline whose stages you
   name `donnees` and `entrainer`; on a fresh clone, once the environment is
   rebuilt from the lock and the data pulled, `dvc repro` gives back the
   metrics of the repository (RMSE 23.31 ms);
3. the training logs on the MLflow server, in a finished run, its parameters,
   its metrics and its model, with the tags `git_commit` (a commit of the
   repository) and `data_sha256` (SHA-256 of `data/metriques.csv`);
4. the model of that run is registered under the name `latence-service`, and
   the alias `challenger` points at the version built by that run;
5. a pytest suite in `tests/` reads the dataset from the environment variable
   `DONNEES` (default `data/metriques.csv`) and the metrics from `METRIQUES`
   (default `metrics.json`), and fails on `casse-schema.csv` (missing
   columns) and on a metrics file whose `rmse` exceeds `rmse_max`, a
   threshold read from the versioned file `seuils.yaml` (at most `28.0`). It
   passes on the repository's own data and metrics.

## What is graded

The state of `projet/`, of the S3 store and of the MLflow server, never the
commands typed: the grader clones your repository, replays the pipeline and
runs your suite on its own datasets and metrics files. No hint is offered:
the exam measures what you already know how to do. Pass mark: 70 points.
