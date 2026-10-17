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

1. the data is versioned by DVC and pushed to the S3 store, whose remote is the
   root of the bucket `dvc-donnees`; the committed `.dvc/config` holds no access
   key (the keys stay in the environment); `dvc status` is clean and the store is
   in sync;
2. the data generation and the training are a DVC pipeline whose stages you
   name `donnees` and `entrainer` (`entrainer` depends on `data/metriques.csv`, each
   stage declares its parameters); on a fresh clone, once the environment is
   rebuilt from the lock and the data pulled, `dvc repro` gives back the
   metrics of the repository (RMSE 23.31 ms);
3. the training logs on the MLflow server, in a finished run, its parameters,
   its metrics (`rmse` and `r2`) and its model, with the tags `git_commit` (a commit of the
   repository) and `data_sha256` (SHA-256 of `data/metriques.csv`);
4. the model of that run is registered under the name `latence-service`, and
   the alias `challenger` points at the version built by that run;
5. a pytest suite in `tests/` reads the dataset from the environment variable
   `DONNEES` (default `data/metriques.csv`), the metrics of the candidate from
   `METRIQUES` (default `metrics.json`) and those of the champion from
   `CHAMPION` (default `metrics-champion.json`, a copy of the file provided
   next to the bundle, committed in the repository). It fails on both broken
   datasets provided, `casse-schema.csv` (missing columns) and
   `casse-bornes.csv` (values out of bounds); on a candidate whose `rmse`
   exceeds `rmse_max`; and on a candidate whose `rmse` exceeds the champion's
   by more than 3 ms. `rmse_max` and `tolerance_ms`, the tolerance against the
   champion, are read from the versioned file `seuils.yaml`: `rmse_max` lets
   your model pass and is at most `28.0`, `tolerance_ms` lets it pass too. The
   suite passes on the repository's own data and metrics.

## What is graded

The state of `projet/`, of the S3 store and of the MLflow server, never the
commands typed: the grader clones your repository, replays the pipeline and
runs your suite on its own datasets and metrics files. No hint is offered:
the exam measures what you already know how to do. Pass mark: 70 points.
