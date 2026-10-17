# Scenario

In this repository, the data is generated with `genere-metriques.py`, then
`train.py` is run, by hand, in that order. Seed and hyperparameters are in
`params.yaml`. When a colleague changes `n_arbres`, nobody knows whether the
data must be regenerated too, and the published metrics could never be redone
by anyone else. The catalogue's S3 stack (bucket `dvc-donnees`,
`http://127.0.0.1:3900`, region `garage`, keys in `shared/socle/.env`) is up.

## Mission

Deliver a repository whose pipeline (data, then training) is described and
versioned, with its outputs in the bucket. A fresh clone, its environment
rebuilt from the lock, must give the same metrics. A `dvc repro` with no change
must replay nothing, and changing `n_arbres` must replay only the training
stage, which you will name `entrainer`.
