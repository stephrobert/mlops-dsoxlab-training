# Scenario

A colleague hands you `train.py`: a model that predicts a service's p95 latency
from its load. She announced an RMSE of 23 ms. You run it twice: you get two
different values, and neither is hers. She no longer remembers which library
versions she had installed, or which dataset she used. `genere-metriques.py`
produces the catalogue's running dataset.

Nobody can say today whether a metric gap comes from the code, the data, the
libraries or chance.

## Mission

Deliver a project whose two trainings give exactly the same metrics, on any
workstation that clones it. Expected dataset: seed 42, 5000 rows, in
`data/metriques.csv`. The project is a clean Git repository, its environment
lives in `.venv`, and the seed is set in `params.yaml` (key `seed`). Finding
where the variation comes from, and what must be versioned so someone else gets
the same result, is your work.
