# Scenario

Last week someone reran the metrics generator onto the same
`data/metriques.csv`. The previous dataset (seed 42) is lost, and the model
trained on it can no longer be rebuilt. Git must not carry the data itself: it
is heavy. The catalogue's S3 stack (Garage, bucket `dvc-donnees`, endpoint
`http://127.0.0.1:3900`, region `garage`, keys in `shared/socle/.env`) is up.

## Mission

In the working directory (repository to initialise, environment with DVC and
its S3 support): version the seed 42 dataset then the seed 43 dataset, in two
separate commits, with the data in the bucket. A fresh clone must restore the
current dataset (seed 43) with `dvc pull`, and going back to the first commit
must restore the seed 42 dataset, byte for byte. The repository stays clean and
the remote configuration travels with it, not the keys.
